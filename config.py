import os
from dotenv import load_dotenv

load_dotenv()

# ------------------------
# API Key
# ------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHAT_MODEL = "llama-3.1-8b-instant"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ------------------------
# Text Splitter
# ------------------------

CHUNK_SIZE = 100

CHUNK_OVERLAP = 20

# ------------------------
# Vector Database
# ------------------------

CHROMA_DB_PATH = "chroma_db"

# ------------------------
# Data
# ------------------------

DOCUMENT_PATH = "data/college_info.txt"