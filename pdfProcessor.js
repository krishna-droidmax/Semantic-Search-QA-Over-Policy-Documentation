const fs = require('fs');
const pdf = require('pdf-parse');
const { pipeline } = require('@xenova/transformers');
const { IndexFlatL2 } = require('faiss-node');
const fetch = require('node-fetch');
require('dotenv').config();

class PDFProcessor {
  constructor() {
    this.chunks = [];
    this.metadata = [];
    this.faissIndex = null;
    this.embedder = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    
    try {
      console.log('Initializing Sentence Transformer...');
      this.embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
      this.faissIndex = new IndexFlatL2(384); // 384 dimensions for all-MiniLM-L6-v2
      this.initialized = true;
      console.log('✅ Sentence Transformer initialized');
    } catch (error) {
      console.error('Failed to initialize embedder:', error);
      throw error;
    }
  }

  async processPDF(filePath) {
    try {
      await this.initialize();
      
      console.log(`Extracting text from PDF: ${filePath}`);
      const dataBuffer = fs.readFileSync(filePath);
      const pdfData = await pdf(dataBuffer);
      
      console.log(`Total text length: ${pdfData.text.length} characters`);
      
      // Split text into chunks
      this.chunks = this.splitIntoChunks(pdfData.text);
      console.log(`Created ${this.chunks.length} chunks`);
      
      // Generate embeddings for each chunk
      console.log('Generating embeddings...');
      const embeddings = [];
      
      for (let i = 0; i < this.chunks.length; i++) {
        const chunk = this.chunks[i];
        const embedding = await this.embedder(chunk, { pooling: 'mean', normalize: true });
        embeddings.push(Array.from(embedding.data));
        
        // Create metadata for this chunk
        this.metadata.push({
          chunkIndex: i,
          startChar: i * 500,
          endChar: Math.min((i + 1) * 500, pdfData.text.length),
          pageNumber: Math.floor(i / 5) + 1 // Approximate page number
        });
      }
      
      // Add embeddings to FAISS index
      if (embeddings.length > 0) {
        const embeddingsArray = new Float32Array(embeddings.flat());
        this.faissIndex.add(embeddingsArray);
        console.log(`✅ Added ${embeddings.length} embeddings to FAISS index`);
      }
      
      console.log('PDF processing completed successfully');
    } catch (error) {
      console.error('PDF processing error:', error);
      throw error;
    }
  }

  splitIntoChunks(text, chunkSize = 500, overlap = 50) {
    const chunks = [];
    let start = 0;
    
    while (start < text.length) {
      let end = start + chunkSize;
      
      // Try to break at sentence boundary
      if (end < text.length) {
        const lastPeriod = text.lastIndexOf('.', end);
        const lastNewline = text.lastIndexOf('\n', end);
        const breakPoint = Math.max(lastPeriod, lastNewline);
        
        if (breakPoint > start + chunkSize * 0.5) {
          end = breakPoint + 1;
        }
      }
      
      const chunk = text.slice(start, end).trim();
      if (chunk.length > 0) {
        chunks.push(chunk);
      }
      
      start = end - overlap;
    }
    
    return chunks;
  }

  async searchSimilarChunks(query, topK = 3) {
    if (!this.initialized || this.chunks.length === 0) {
      return [];
    }

    try {
      // Generate embedding for query
      const queryEmbedding = await this.embedder(query, { pooling: 'mean', normalize: true });
      const queryVector = new Float32Array(Array.from(queryEmbedding.data));
      
      // Search in FAISS index
      const { distances, indices } = this.faissIndex.search(queryVector, topK);
      
      const results = [];
      for (let i = 0; i < indices.length; i++) {
        if (indices[i] >= 0 && indices[i] < this.chunks.length) {
          results.push({
            chunk: this.chunks[indices[i]],
            metadata: this.metadata[indices[i]],
            similarity: 1 - distances[i] // Convert distance to similarity
          });
        }
      }
      
      return results;
    } catch (error) {
      console.error('Search error:', error);
      return [];
    }
  }

  async queryPerplexity(query, context) {
    const apiKey = process.env.PERPLEXITY_API_KEY;
    if (!apiKey) {
      throw new Error('Perplexity API key not found');
    }

    const prompt = `Based on the following context from a PDF document, please answer the question. Provide a comprehensive and well-formatted answer using markdown formatting.

Context:
${context}

Question: ${query}

Please provide a detailed answer based on the context above. Use markdown formatting for better readability.`;

    try {
      const response = await fetch('https://api.perplexity.ai/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'sonar-pro',
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: 1000,
          temperature: 0.2
        })
      });

      if (!response.ok) {
        throw new Error(`Perplexity API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;
    } catch (error) {
      console.error('Perplexity API error:', error);
      throw error;
    }
  }

  async query(userQuery) {
    try {
      console.log(`Processing query: '${userQuery}'`);
      console.log(`Available chunks: ${this.chunks.length}`);
      
      // Search for similar chunks
      const similarChunks = await this.searchSimilarChunks(userQuery, 3);
      console.log(`Found ${similarChunks.length} similar chunks`);
      
      if (similarChunks.length === 0) {
        throw new Error('No relevant chunks found');
      }
      
      // Combine context from similar chunks
      const context = similarChunks.map(chunk => chunk.chunk).join('\n\n');
      console.log(`Context length: ${context.length} characters`);
      
      // Query Perplexity API
      console.log('Sending request to Perplexity API...');
      const answer = await this.queryPerplexity(userQuery, context);
      console.log('Successfully received response from Perplexity API');
      
      // Format response
      const formattedResponse = {
        answer: answer,
        sources: similarChunks.map((chunk, index) => ({
          rank: index + 1,
          content: chunk.chunk.substring(0, 200) + '...',
          metadata: chunk.metadata,
          similarity: chunk.similarity
        })),
        metadata: {
          totalChunks: this.chunks.length,
          relevantChunks: similarChunks.length,
          query: userQuery,
          timestamp: new Date().toISOString()
        },
        supporting_chunks: similarChunks.map(chunk => chunk.chunk) // For backward compatibility
      };
      
      return formattedResponse;
    } catch (error) {
      console.error('Query processing error:', error);
      throw error;
    }
  }

  hasDocument() {
    return this.chunks.length > 0;
  }

  getChunksCount() {
    return this.chunks.length;
  }
}

module.exports = PDFProcessor;

