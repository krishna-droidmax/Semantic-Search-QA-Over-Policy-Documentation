# PDF RAG System - Python Edition

A powerful PDF Question-Answering system built with Python, using modern NLP libraries for text extraction, embeddings, and semantic search.

## Features

- **PDF Text Extraction**: Uses both `pdfplumber` and `PyMuPDF` for robust text extraction
- **Advanced Embeddings**: Leverages `SentenceTransformers` (HuggingFace) for high-quality embeddings
- **Semantic Search**: Uses `FAISS` for fast and accurate similarity search
- **AI-Powered Q&A**: Integrates with Perplexity Pro API for intelligent question answering
- **Modern Web Interface**: Clean, responsive Flask-based web application
- **RAG Architecture**: Retrieval-Augmented Generation for accurate, context-aware answers

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **Text Extraction**: pdfplumber, PyMuPDF (fitz)
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **LLM**: Perplexity Pro API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file and add your Perplexity API key:
   ```
   PPLX_API_KEY=your_perplexity_api_key_here
   PORT=5000
   NODE_ENV=development
   ```

3. **Run the Application**:
   ```bash
   python run.py
   ```

   Or directly:
   ```bash
   python app.py
   ```

## Usage

1. **Start the Server**: Run `python run.py`
2. **Open Browser**: Navigate to `http://localhost:5000`
3. **Upload PDF**: Drag and drop or click to upload a PDF file
4. **Ask Questions**: Type your questions about the PDF content
5. **Get Answers**: Receive AI-powered answers with supporting text snippets

## API Endpoints

- `POST /pdf/upload` - Upload and process a PDF file
- `POST /pdf/query` - Query the uploaded PDF
- `GET /pdf/status` - Get current system status
- `POST /pdf/clear` - Clear current PDF data

## Architecture

### Text Processing Pipeline

1. **PDF Upload** → File validation and storage
2. **Text Extraction** → pdfplumber/PyMuPDF extracts text
3. **Text Chunking** → Split text into overlapping chunks
4. **Embedding Generation** → SentenceTransformers creates embeddings
5. **Index Creation** → FAISS builds searchable index

### Query Processing Pipeline

1. **Query Input** → User question
2. **Query Embedding** → Convert question to embedding
3. **Similarity Search** → FAISS finds relevant chunks
4. **Context Building** → Combine relevant chunks
5. **LLM Query** → Send to Perplexity API with context
6. **Response** → Return answer with supporting evidence

## Configuration

### Environment Variables

- `PPLX_API_KEY`: Your Perplexity API key (required)
- `PORT`: Server port (default: 5000)
- `NODE_ENV`: Environment mode (development/production)

### Model Configuration

The system uses `all-MiniLM-L6-v2` by default, which provides:
- 384-dimensional embeddings
- Fast inference
- Good quality for most use cases

You can change the model in `pdf_processor.py`:
```python
pdf_processor = PDFRAGProcessor(model_name="your-preferred-model")
```

## Performance

- **Text Extraction**: ~1-2 seconds per page
- **Embedding Generation**: ~0.1-0.5 seconds per chunk
- **Query Processing**: ~2-5 seconds total
- **Memory Usage**: ~100-500MB depending on PDF size

## Troubleshooting

### Common Issues

1. **"No PDF has been processed yet"**
   - Upload a PDF file first before asking questions

2. **"Perplexity API key not configured"**
   - Set your API key in the `.env` file

3. **Import errors**
   - Install all dependencies: `pip install -r requirements.txt`

4. **PDF extraction fails**
   - Try different PDF files
   - Check if PDF is password-protected or corrupted

### Debug Mode

Run with debug mode for detailed logging:
```bash
NODE_ENV=development python app.py
```

## Comparison with Node.js Version

| Feature | Node.js Version | Python Version |
|---------|----------------|----------------|
| Text Extraction | pdf-parse | pdfplumber + PyMuPDF |
| Embeddings | @xenova/transformers | SentenceTransformers |
| Vector Search | faiss-node | FAISS |
| Performance | Good | Excellent |
| Reliability | Moderate | High |
| Maintenance | Complex | Simple |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on GitHub
4. Contact the development team
