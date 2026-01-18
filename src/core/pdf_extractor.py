import os
import logging
from pypdf import PdfReader

# Try to import LlamaParse, but don't fail if it's not installed (though we installed it)
try:
    from llama_parse import LlamaParse
    import nest_asyncio
    nest_asyncio.apply() # Apply nest_asyncio to allow nested event loops if needed
    HAS_LLAMA_PARSE = True
except ImportError:
    HAS_LLAMA_PARSE = False

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.
    
    Tries to use LlamaParse first if LLAMA_CLOUD_API_KEY is present in env.
    Falls back to pypdf if key is missing or LlamaParse fails.
    """
    llama_key = os.getenv("LLAMA_CLOUD_API_KEY")
    
    if HAS_LLAMA_PARSE and llama_key:
        try:
            logger.info("Using LlamaParse for PDF extraction...")
            parser = LlamaParse(
                result_type="markdown",  # "markdown" and "text" are available
                api_key=llama_key,
                verbose=True,
                language="fr" # Optional: could make this configurable
            )
            
            # LlamaParse.load_data returns a list of Document objects
            documents = parser.load_data(file_path)
            
            full_text = "\n\n".join([doc.text for doc in documents])
            
            if full_text.strip():
                logger.info(f"LlamaParse successfully extracted {len(full_text)} chars.")
                return full_text
            else:
                logger.warning("LlamaParse returned empty text. Falling back to pypdf.")
                
        except Exception as e:
            logger.error(f"LlamaParse failed: {e}. Falling back to pypdf.")
    
    # Fallback to pypdf
    logger.info("Using pypdf for PDF extraction.")
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise ValueError(f"Error reading PDF file: {str(e)}")
