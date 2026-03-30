# Copy this file to config.py and fill in your actual API key
# config.py is git-ignored to keep secrets off GitHub

OPENROUTER_API_KEY = "your-openrouter-api-key-here"
OPENROUTER_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"
OPENROUTER_FALLBACK_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:7b"
UPLOAD_FOLDER = "static/uploads"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

CHROMA_PERSIST_DIR = "chroma_store"
CHROMA_COLLECTION  = "marketing_docs"
EMBED_MODEL        = "nomic-embed-text"
RAG_CHUNK_SIZE     = 400        # characters per chunk
RAG_CHUNK_OVERLAP  = 80         # overlap between adjacent chunks
RAG_TOP_K          = 4          # chunks retrieved per campaign query
DOC_UPLOAD_FOLDER  = "static/doc_uploads"
MAX_DOC_SIZE       = 10 * 1024 * 1024
