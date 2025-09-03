const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

// Import PDF processor
const PDFProcessor = require('./pdfProcessor');

const pdfProcessor = new PDFProcessor();

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/pdf/status', (req, res) => {
  res.json({
    status: 'ready',
    hasDocument: pdfProcessor.hasDocument(),
    chunksCount: pdfProcessor.getChunksCount()
  });
});

app.post('/pdf/upload', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file uploaded' });
    }

    console.log(`Processing PDF: ${req.file.filename}`);
    await pdfProcessor.processPDF(req.file.path);
    
    res.json({ 
      message: 'PDF processed successfully',
      filename: req.file.filename,
      chunksCount: pdfProcessor.getChunksCount()
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Failed to process PDF' });
  }
});

app.post('/pdf/query', async (req, res) => {
  try {
    const { query } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    if (!pdfProcessor.hasDocument()) {
      return res.status(400).json({ error: 'No document loaded' });
    }

    console.log(`Processing query: ${query}`);
    const result = await pdfProcessor.query(query);
    
    res.json(result);
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ error: 'Failed to process query' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log('🚀 Starting PDF RAG System - Node.js Edition');
  console.log('==================================================');
  console.log('✅ Perplexity API key found');
  console.log(`🚀 Starting Express server on port ${PORT}`);
  console.log(`📱 Open your browser to: http://localhost:${PORT}`);
  console.log('==================================================');
});

