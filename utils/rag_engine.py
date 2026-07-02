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
    search_type="mmr",
    search_kwargs={
        "k":4,
        "fetch_k":10,
        "lambda_mult":0.5
    }
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

    print("\n" + "=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    for i, doc in enumerate(docs, 1):
        print(f"\nDOCUMENT {i}")
        print("SOURCE:", doc.metadata.get("source"))
        print("-" * 50)
        print(doc.page_content)
        print("-" * 50)

    # Build context AFTER printing all documents
    context = "\n\n".join(
        [f"Document {i}:\n{doc.page_content}" for i, doc in enumerate(docs, 1)]
    )

    sources = []
    seen = set()

    for doc in docs:
        source = doc.metadata.get("source", "")
        source = os.path.basename(source.replace("\\", "/"))

        if source not in seen:
            seen.add(source)
            sources.append(source)

    prompt = f"""
You are College AI Assistant.

You are an AI assistant that answers questions about ABC Institute of Technology.

Use ONLY the information provided in the context.

Instructions:
- Answer clearly and naturally.
- Combine information from multiple documents whenever relevant.
- Use bullet points for lists.
- Write complete sentences.
- Never mention "Document 1", "Document 2", or "context".
- Do not make up information.
- If the answer is not found in the context, reply exactly:

I don't have that information.

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