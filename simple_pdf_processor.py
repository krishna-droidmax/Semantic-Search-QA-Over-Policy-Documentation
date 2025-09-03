import os
import json
import pdfplumber
import requests
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplePDFProcessor:
    def __init__(self):
        """Initialize the simple PDF processor"""
        self.chunks = []
        self.chunk_metadata = []
        
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        logger.info(f"Extracting text from PDF: {pdf_path}")
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num} ---\n{page_text}\n"
                        logger.info(f"Extracted text from page {page_num}")
            
            logger.info(f"Total text length: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk in words
            overlap: Number of words to overlap between chunks
            
        Returns:
            List of text chunks
        """
        logger.info("Splitting text into chunks")
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def process_pdf(self, pdf_path: str, chunk_size: int = 1000, overlap: int = 200) -> Dict:
        """
        Process a PDF file: extract text and chunk
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Size of text chunks
            overlap: Overlap between chunks
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract text
            text = self.extract_text(pdf_path)
            if not text.strip():
                raise ValueError("No text extracted from PDF")
            
            # Split into chunks
            self.chunks = self.split_into_chunks(text, chunk_size, overlap)
            if not self.chunks:
                raise ValueError("No chunks created from text")
            
            # Create metadata
            self.chunk_metadata = []
            for i, chunk in enumerate(self.chunks):
                # Estimate page number based on chunk position
                estimated_page = (i / len(self.chunks)) * 10 + 1  # Rough estimate
                self.chunk_metadata.append({
                    'text': chunk,
                    'chunk_index': i,
                    'estimated_page': int(estimated_page)
                })
            
            logger.info("PDF processing completed successfully")
            
            return {
                'success': True,
                'chunks_count': len(self.chunks),
                'text_length': len(text),
                'message': f"Successfully processed PDF with {len(self.chunks)} chunks"
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Enhanced keyword-based search for similar chunks
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of similar chunks with metadata
        """
        if not self.chunks:
            raise ValueError("No PDF has been processed yet. Please process a PDF first.")
        
        logger.info(f"Searching for chunks matching: {query}")
        logger.info(f"Total chunks available: {len(self.chunks)}")
        
        # Enhanced keyword matching with multiple strategies
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Remove common stop words for better matching
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        query_words = query_words - stop_words
        
        chunk_scores = []
        
        for i, chunk in enumerate(self.chunks):
            chunk_lower = chunk.lower()
            chunk_words = set(chunk_lower.split())
            
            # Strategy 1: Exact word overlap
            overlap = len(query_words.intersection(chunk_words))
            word_score = overlap / max(len(query_words), 1) if query_words else 0
            
            # Strategy 2: Substring matching (for partial word matches)
            substring_score = 0
            for word in query_words:
                if word in chunk_lower:
                    substring_score += 1
            substring_score = substring_score / max(len(query_words), 1) if query_words else 0
            
            # Strategy 3: Phrase matching (for multi-word queries)
            phrase_score = 0
            if len(query_words) > 1:
                query_phrase = query_lower
                if query_phrase in chunk_lower:
                    phrase_score = 1.0
            
            # Combined score with weights
            total_score = (word_score * 0.5) + (substring_score * 0.3) + (phrase_score * 0.2)
            
            # Include chunks with any score > 0, or if no matches found, include first few chunks
            if total_score > 0:
                chunk_scores.append((i, total_score))
            elif len(chunk_scores) == 0 and i < 3:  # Fallback: include first 3 chunks if no matches
                chunk_scores.append((i, 0.1))
        
        # If still no matches, return first few chunks as fallback
        if not chunk_scores:
            logger.warning("No keyword matches found, returning first few chunks as fallback")
            for i in range(min(3, len(self.chunks))):
                chunk_scores.append((i, 0.05))
        
        # Sort by score and take top_k
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        top_chunks = chunk_scores[:top_k]
        
        logger.info(f"Found {len(top_chunks)} relevant chunks")
        
        # Get results
        results = []
        for i, (idx, score) in enumerate(top_chunks):
            result = {
                'chunk_index': idx,
                'text': self.chunk_metadata[idx]['text'],
                'estimated_page': self.chunk_metadata[idx]['estimated_page'],
                'similarity_score': score,
                'rank': i + 1
            }
            results.append(result)
        
        return results
    
    def query_perplexity(self, prompt: str, api_key: str) -> Dict:
        """
        Query Perplexity API with fallback models
        
        Args:
            prompt: The prompt to send
            api_key: Perplexity API key
            
        Returns:
            Response from Perplexity API
        """
        # List of models to try in order (current Perplexity models)
        models_to_try = [
            "sonar-pro",
            "sonar-reasoning",
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-huge-128k-online",
            "llama-3.1-sonar-small-128k-chat",
            "llama-3.1-sonar-large-128k-chat",
            "llama-3.1-sonar-huge-128k-chat"
        ]
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        for model in models_to_try:
            try:
                data = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based only on the provided context. If the context doesn't contain enough information to answer the question, say so."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
                
                logger.info(f"Trying model: {model}")
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Success with model: {model}")
                    return {
                        'success': True,
                        'answer': result['choices'][0]['message']['content'],
                        'model': result['model'],
                        'usage': result.get('usage', {})
                    }
                else:
                    logger.warning(f"❌ Model {model} failed: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                logger.warning(f"❌ Model {model} exception: {e}")
                continue
        
        # If all models failed
        logger.error("All models failed")
        return {
            'success': False,
            'error': 'All Perplexity models failed. Please check your API key and account status.'
        }
    
    def query_pdf(self, question: str, api_key: str, top_k: int = 5) -> Dict:
        """
        Query the PDF using enhanced keyword matching + Perplexity API
        
        Args:
            question: User's question
            api_key: Perplexity API key
            top_k: Number of similar chunks to retrieve
            
        Returns:
            Dictionary with answer and supporting chunks
        """
        try:
            logger.info(f"Processing query: '{question}'")
            logger.info(f"Available chunks: {len(self.chunks)}")
            
            # Search for similar chunks
            similar_chunks = self.search_similar_chunks(question, top_k)
            
            if not similar_chunks:
                logger.error("No similar chunks found")
                return {
                    'success': False,
                    'error': 'No relevant chunks found. Please try a different question or check if the PDF was processed correctly.'
                }
            
            logger.info(f"Found {len(similar_chunks)} similar chunks")
            
            # Create context from similar chunks
            context = "\n\n".join([
                f"Page {chunk['estimated_page']}: {chunk['text'][:500]}..."
                for chunk in similar_chunks
            ])
            
            logger.info(f"Context length: {len(context)} characters")
            
            # Create RAG prompt with better formatting instructions
            rag_prompt = f"""Based on the following PDF context, please provide a comprehensive and well-formatted answer to the user's question. 

Instructions:
- Use only information from the provided context
- Format your response with clear headings, bullet points, or numbered lists when appropriate
- If the context doesn't contain enough information, clearly state this
- Be thorough but concise
- Use markdown formatting for better readability

Context:
{context}

User Question: {question}

Please provide a well-formatted answer:"""
            
            logger.info("Sending request to Perplexity API...")
            
            # Query Perplexity API
            perplexity_response = self.query_perplexity(rag_prompt, api_key)
            
            if perplexity_response['success']:
                logger.info("Successfully received response from Perplexity API")
                
                # Format the response with additional metadata
                formatted_response = {
                    'success': True,
                    'answer': perplexity_response['answer'],
                    'question': question,
                    'model': perplexity_response.get('model', 'unknown'),
                    'usage': perplexity_response.get('usage', {}),
                    'supporting_chunks': similar_chunks,  # Keep for backward compatibility
                    'sources': {
                        'chunks_used': len(similar_chunks),
                        'total_chunks': len(self.chunks),
                        'chunk_details': [
                            {
                                'rank': chunk['rank'],
                                'page': chunk['estimated_page'],
                                'relevance_score': f"{chunk['similarity_score']:.2f}",
                                'preview': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
                            }
                            for chunk in similar_chunks
                        ]
                    },
                    'metadata': {
                        'context_length': len(context),
                        'processing_time': 'N/A',  # Could add timing if needed
                        'search_strategy': 'Enhanced keyword matching'
                    }
                }
                
                return formatted_response
            else:
                logger.error(f"Perplexity API error: {perplexity_response['error']}")
                return {
                    'success': False,
                    'error': f"Perplexity API error: {perplexity_response['error']}"
                }
                
        except Exception as e:
            logger.error(f"Error querying PDF: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"Internal error: {str(e)}"
            }
