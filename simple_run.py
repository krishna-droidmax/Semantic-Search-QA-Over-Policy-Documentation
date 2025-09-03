#!/usr/bin/env python3
"""
PDF RAG System - Simple Edition
Run this script to start the Flask application with basic functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main function to run the application"""
    print("🚀 Starting PDF RAG System - Simple Edition")
    print("=" * 50)
    
    # Check if required environment variables are set
    api_key = os.getenv('PPLX_API_KEY')
    if not api_key:
        print("❌ Error: PPLX_API_KEY not found in environment variables")
        print("Please set your Perplexity API key in the .env file")
        sys.exit(1)
    
    print("✅ Perplexity API key found")
    
    # Check if uploads directory exists
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"✅ Created uploads directory: {uploads_dir}")
    
    # Import and run the Flask app
    try:
        from simple_app import app
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('NODE_ENV', 'development') == 'development'
        
        print(f"🚀 Starting Flask server on port {port}")
        print(f"📱 Open your browser to: http://localhost:{port}")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages: pip install flask flask-cors pdfplumber requests python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
