from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from simple_pdf_processor import SimplePDFProcessor
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize PDF processor
pdf_processor = SimplePDFProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main HTML page"""
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/pdf/upload', methods=['POST'])
def upload_pdf():
    """Upload and process a PDF file"""
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Processing PDF: {filename}")
        
        # Process PDF
        result = pdf_processor.process_pdf(filepath)
        
        if result['success']:
            return jsonify({
                'message': 'PDF processed successfully',
                'filename': filename,
                'chunks': result['chunks_count'],
                'text_length': result['text_length']
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/pdf/query', methods=['POST'])
def query_pdf():
    """Query the uploaded PDF"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Get API key from environment
        api_key = os.getenv('PPLX_API_KEY')
        if not api_key:
            return jsonify({'error': 'Perplexity API key not configured'}), 500
        
        logger.info(f"Processing query: {query}")
        
        # Query PDF
        result = pdf_processor.query_pdf(query, api_key)
        
        if result['success']:
            return jsonify({
                'answer': result['answer'],
                'supporting_chunks': result.get('supporting_chunks', []),
                'question': result['question'],
                'model': result.get('model', 'unknown'),
                'sources': result.get('sources', {}),
                'metadata': result.get('metadata', {})
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/pdf/status', methods=['GET'])
def get_status():
    """Get the current status of the PDF processor"""
    try:
        has_pdf = len(pdf_processor.chunks) > 0
        chunks_count = len(pdf_processor.chunks)
        
        return jsonify({
            'has_pdf': has_pdf,
            'chunks_count': chunks_count,
            'model_name': 'Simple Keyword Search',
            'dimension': 'N/A'
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/pdf/clear', methods=['POST'])
def clear_pdf():
    """Clear the current PDF data"""
    try:
        pdf_processor.chunks = []
        pdf_processor.chunk_metadata = []
        
        return jsonify({'message': 'PDF data cleared successfully'})
    except Exception as e:
        logger.error(f"Clear error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/pdf/debug', methods=['GET'])
def debug_pdf():
    """Debug endpoint to check PDF processing status"""
    try:
        debug_info = {
            'chunks_count': len(pdf_processor.chunks),
            'chunk_metadata_count': len(pdf_processor.chunk_metadata),
            'has_chunks': len(pdf_processor.chunks) > 0,
            'sample_chunk': pdf_processor.chunks[0][:200] + '...' if pdf_processor.chunks else None,
            'sample_metadata': pdf_processor.chunk_metadata[0] if pdf_processor.chunk_metadata else None
        }
        
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
