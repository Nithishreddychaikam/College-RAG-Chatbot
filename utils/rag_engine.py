import os

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from config import (
    GROQ_API_KEY,
    CHAT_MODEL,
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
)

# -----------------------------
# Embedding Model
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

# -----------------------------
# Load Existing ChromaDB
# -----------------------------
vectorstore = Chroma(
    persist_directory=CHROMA_DB_PATH,
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 2}
)

# -----------------------------
# Groq LLM
# -----------------------------
llm = ChatGroq(
    model=CHAT_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0
)

# -----------------------------
# Ask Question Function
# -----------------------------
def ask_question(question):

    docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in docs])

    sources = []
    seen = set()

    for doc in docs:
        source = doc.metadata.get("source", "")
        source = os.path.basename(source.replace("\\", "/"))

        if source not in seen:
            seen.add(source)
            sources.append(source)

    prompt = f"""
You are a helpful college assistant.

Answer ONLY using the context below.

If the answer cannot be found completely in the provided context,
reply exactly:

I don't have that information.

Do not use outside knowledge.
Do not guess.
Do not make up information.
Answer only from the context.

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": sources
    }