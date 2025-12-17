"""
Document Processing Utilities
"""
import pdfplumber
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string
    """
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        full_text = "\n\n".join(text_parts)
        logger.info("Extracted %d characters from %s", len(full_text), Path(pdf_path).name)
        return full_text
    
    except Exception as exc:
        logger.error("Error extracting text from %s: %s", pdf_path, exc)
        return ""


def extract_tables_from_pdf(pdf_path: str) -> List[List[List[str]]]:
    """
    Extract tables from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of tables, where each table is a list of rows
    """
    try:
        all_tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
        
        logger.info("Extracted %d tables from %s", len(all_tables), Path(pdf_path).name)
        return all_tables
    
    except Exception as exc:
        logger.error("Error extracting tables from %s: %s", pdf_path, exc)
        return []


def process_tender_documents(document_paths: List[str]) -> Dict[str, str]:
    """
    Process multiple tender documents and extract text.
    
    Args:
        document_paths: List of paths to document files
        
    Returns:
        Dictionary mapping document path to extracted text
    """
    extracted_texts = {}
    
    for doc_path in document_paths:
        path = Path(doc_path)
        
        if path.suffix.lower() == '.pdf':
            text = extract_text_from_pdf(doc_path)
            extracted_texts[doc_path] = text
        else:
            logger.warning("Unsupported file format: %s", path.suffix)
            extracted_texts[doc_path] = ""
    
    return extracted_texts
