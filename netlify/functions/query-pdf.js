const { Handler } = require('@netlify/functions');
const fetch = require('node-fetch');

// This would be shared with the upload function in a real implementation
let pdfData = null;
let faissIndex = null;
let embedder = null;
let chunks = [];
let metadata = [];

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
    const { query } = JSON.parse(event.body);
    
    if (!query) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Query is required' }),
      };
    }

    if (!pdfData || chunks.length === 0) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'No document loaded. Please upload a PDF first.' }),
      };
    }

    console.log(`Processing query: '${query}'`);

    // For demo purposes, return a simulated response
    const simulatedAnswer = `
    Based on the uploaded document, here's what I found regarding your question: "${query}"

    The document contains information about various topics that can be queried. 
    It includes multiple sections with different content that users can ask questions about.

    **Key Points:**
    - The document is structured with multiple sections
    - Content covers various topics for querying
    - Users can get relevant answers based on the document content

    This is a demonstration response. In a full implementation, this would use 
    semantic search to find relevant chunks and generate answers using an LLM.
    `;

    const simulatedSources = [
      {
        rank: 1,
        content: "This is a sample PDF document for demonstration purposes...",
        metadata: { chunkIndex: 0, pageNumber: 1 },
        similarity: 0.95
      },
      {
        rank: 2,
        content: "It contains information about various topics that can be queried...",
        metadata: { chunkIndex: 1, pageNumber: 1 },
        similarity: 0.87
      }
    ];

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        answer: simulatedAnswer,
        sources: simulatedSources,
        metadata: {
          totalChunks: chunks.length,
          relevantChunks: simulatedSources.length,
          query: query,
          timestamp: new Date().toISOString()
        }
      }),
    };

  } catch (error) {
    console.error('Query error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Failed to process query' }),
    };
  }
};

module.exports = { handler };
