import glob
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader
)

from config import (
    DOCUMENT_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    CHROMA_DB_PATH
)

print("=" * 60)
print("Creating Vector Database")
print("=" * 60)

# Load document
documents = []

# -----------------------------
# Load TXT Files
# -----------------------------
txt_files = glob.glob("data/*.txt")

for file in txt_files:

    loader = TextLoader(
        file,
        encoding="utf-8"
    )

    documents.extend(loader.load())

# -----------------------------
# Load PDF Files
# -----------------------------
pdf_files = glob.glob("data/*.pdf")

for file in pdf_files:

    loader = PyPDFLoader(file)

    documents.extend(loader.load())

print(f"Loaded {len(documents)} document(s).")

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks.")

# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

print("Embedding model loaded.")

# Create ChromaDB
Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=CHROMA_DB_PATH
)

print("\n✅ Vector Database Created Successfully!")