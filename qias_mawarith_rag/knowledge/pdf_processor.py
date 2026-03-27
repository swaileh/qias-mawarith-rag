"""
PDF Processor for Islamic Law Documents
Handles Arabic text extraction, cleaning, and chunking
"""

from pathlib import Path
from typing import List, Dict, Any
import yaml
import fitz  # PyMuPDF
import pdfplumber
from dataclasses import dataclass


@dataclass
class Document:
    """Represents a processed document chunk"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str


class PDFProcessor:
    """Process PDF documents for the RAG knowledge base"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize PDF processor with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.pdf_config = self.config['pdf']
        self.vector_config = self.config['vector_store']
        self.chunk_size = self.vector_config['chunk_size']
        self.chunk_overlap = self.vector_config['chunk_overlap']
    
    def extract_text_pymupdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF using PyMuPDF (better for Arabic)"""
        pages = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Handle Arabic text reshaping if needed
            if self.pdf_config.get('arabic_text_processing', True):
                text = self._process_arabic_text(text)
            
            pages.append({
                'page_number': page_num + 1,
                'text': text,
                'char_count': len(text)
            })
        
        doc.close()
        return pages
    
    def extract_text_pdfplumber(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF using pdfplumber (better for tables)"""
        pages = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                # Extract tables if configured
                if self.pdf_config.get('extract_tables', True):
                    tables = page.extract_tables()
                    if tables:
                        text += "\n\n[Tables extracted]\n"
                        for table in tables:
                            text += "\n" + self._format_table(table)
                
                pages.append({
                    'page_number': page_num + 1,
                    'text': text,
                    'char_count': len(text)
                })
        
        return pages
    
    def _process_arabic_text(self, text: str) -> str:
        """Process Arabic text for proper display and storage"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Note: reshape and get_display are for rendering only
        # We store original text for better search
        return text
    
    def _format_table(self, table: List[List[str]]) -> str:
        """Format extracted table as text"""
        if not table:
            return ""
        
        formatted = []
        for row in table:
            row_text = " | ".join([cell or "" for cell in row])
            formatted.append(row_text)
        
        return "\n".join(formatted)
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """Split text into overlapping chunks"""
        # Simple character-based chunking
        # TODO: Improve with sentence-aware chunking for Arabic
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary (. or ، or ؛)
            if end < len(text):
                # Look for Arabic or English sentence terminators
                for sep in ['. ', '.\n', '، ', '؛ ']:
                    split_pos = chunk_text.rfind(sep)
                    if split_pos > self.chunk_size * 0.7:  # At least 70% through
                        end = start + split_pos + len(sep)
                        chunk_text = text[start:end]
                        break
            
            # Create document chunk
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = chunk_index
            chunk_metadata['char_start'] = start
            chunk_metadata['char_end'] = end
            
            chunk_id = f"{metadata.get('source', 'unknown')}_{chunk_index}"
            
            chunks.append(Document(
                content=chunk_text.strip(),
                metadata=chunk_metadata,
                chunk_id=chunk_id
            ))
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            chunk_index += 1
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Process a single PDF file into document chunks"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Extract text (try PyMuPDF first, fallback to pdfplumber)
        try:
            pages = self.extract_text_pymupdf(str(pdf_path))
        except Exception as e:
            print(f"PyMuPDF failed, using pdfplumber: {e}")
            pages = self.extract_text_pdfplumber(str(pdf_path))
        
        # Combine all pages
        full_text = "\n\n".join([p['text'] for p in pages])
        
        # Create metadata
        metadata = {
            'source': pdf_path.name,
            'source_type': 'pdf',
            'total_pages': len(pages),
            'total_chars': len(full_text),
            'file_path': str(pdf_path)
        }
        
        # Chunk the text
        documents = self.chunk_text(full_text, metadata)
        
        print(f"Processed {pdf_path.name}: {len(documents)} chunks from {len(pages)} pages")
        
        return documents
    
    def process_directory(self, directory_path: str = None) -> List[Document]:
        """Process all PDFs in a directory"""
        if directory_path is None:
            directory_path = self.pdf_config['source_directory']
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_documents = []
        pdf_files = list(directory.glob("*.pdf"))
        
        print(f"Found {len(pdf_files)} PDF files in {directory}")
        
        for pdf_file in pdf_files:
            try:
                documents = self.process_pdf(str(pdf_file))
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")
        
        print(f"Total documents created: {len(all_documents)}")
        
        return all_documents


if __name__ == "__main__":
    # Test the PDF processor
    processor = PDFProcessor()
    
    # Process a directory
    # documents = processor.process_directory("./data/pdfs")
    
    print("PDF Processor initialized successfully")
