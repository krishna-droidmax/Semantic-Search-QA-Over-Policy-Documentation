const { Handler } = require('@netlify/functions');
const multer = require('multer');
const pdf = require('pdf-parse');
const { pipeline } = require('@xenova/transformers');
const { IndexFlatL2 } = require('faiss-node');

// In-memory storage for demo purposes
let pdfData = null;
let faissIndex = null;
let embedder = null;
let chunks = [];
let metadata = [];

const upload = multer({ storage: multer.memoryStorage() });

const handler = async (event, context) => {
  // Handle CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
  };

  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    // Initialize embedder if not already done
    if (!embedder) {
      console.log('Initializing Sentence Transformer...');
      embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
      faissIndex = new IndexFlatL2(384);
      console.log('✅ Sentence Transformer initialized');
    }

    // Parse multipart form data
    const contentType = event.headers['content-type'] || '';
    if (!contentType.includes('multipart/form-data')) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Content-Type must be multipart/form-data' }),
      };
    }

    // For demo purposes, we'll simulate PDF processing
    // In a real implementation, you'd parse the multipart data
    const simulatedPdfText = `
    This is a sample PDF document for demonstration purposes.
    It contains information about various topics that can be queried.
    The document includes multiple sections with different content.
    Users can ask questions about this content and get relevant answers.
    `;

    // Split into chunks
    chunks = splitIntoChunks(simulatedPdfText);
    console.log(`Created ${chunks.length} chunks`);

    // Generate embeddings
    const embeddings = [];
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      const embedding = await embedder(chunk, { pooling: 'mean', normalize: true });
      embeddings.push(Array.from(embedding.data));
      
      metadata.push({
        chunkIndex: i,
        startChar: i * 500,
        endChar: Math.min((i + 1) * 500, simulatedPdfText.length),
        pageNumber: Math.floor(i / 5) + 1
      });
    }

    // Add to FAISS index
    if (embeddings.length > 0) {
      const embeddingsArray = new Float32Array(embeddings.flat());
      faissIndex.add(embeddingsArray);
      console.log(`✅ Added ${embeddings.length} embeddings to FAISS index`);
    }

    pdfData = {
      text: simulatedPdfText,
      chunks: chunks,
      metadata: metadata
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        message: 'PDF processed successfully',
        chunksCount: chunks.length
      }),
    };

  } catch (error) {
    console.error('Upload error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Failed to process PDF' }),
    };
  }
};

function splitIntoChunks(text, chunkSize = 500, overlap = 50) {
  const chunks = [];
  let start = 0;
  
  while (start < text.length) {
    let end = start + chunkSize;
    
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

module.exports = { handler };
