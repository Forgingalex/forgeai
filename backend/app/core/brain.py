"""AI brain functions - PDF processing, summarization, and RAG."""
import httpx
from app.core.config import settings

import io
import time
from typing import List
from pypdf import PdfReader

# Knowledge Base helpers
from app.core.kb import add_texts_to_index, query_kb, clear_kb


#  AI CLIENT - Ollama (Free, Local, Unlimited)

def ask_brain(prompt: str) -> str:
    """Single-shot chat completion via Ollama."""
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")


#  TEXT CHUNKING

def split_text_to_chunks(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks for processing."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    L = len(text)

    while start < L:
        end = min(start + chunk_size, L)
        chunks.append(text[start:end].strip())
        start = end - overlap

    return chunks


#  PDF TEXT EXTRACTION

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using BytesIO + pypdf."""
    try:
        fp = io.BytesIO(pdf_bytes)
        reader = PdfReader(fp)
        texts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)

        return "\n\n".join(texts)

    except Exception:
        return ""


#  SUMMARIZATION ENGINE

def summarize_pdf(pdf_bytes: bytes, simple: bool = False) -> str:
    """Summarize PDF using short chunks for processing."""
    
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("utf-8")

    full_text = extract_text_from_pdf_bytes(pdf_bytes)
    if not full_text.strip():
        return "Could not extract text from this PDF. It may be scanned or unreadable."

    chunks = split_text_to_chunks(full_text, chunk_size=1000, overlap=100)

    short_summaries = []

    for chunk in chunks:
        prompt = (
            "Summarize this text in **3 bullet points**, each under 15 words.\n\n"
            f"{chunk}"
        )
        try:
            summary = ask_brain(prompt)
        except:
            time.sleep(1)
            summary = ask_brain(prompt)

        summary = "\n".join(summary.split("\n")[:3])
        short_summaries.append(summary)

    combined = "\n".join(short_summaries)

    # Final combined synthesis
    synth_prompt = (
        "Using the following bullet summaries, produce:\n"
        "1) One short 5-sentence summary\n"
        "2) 2 real-world examples\n"
        "3) 4 exam-style questions\n\n"
        f"{combined}"
    )

    final_summary = ask_brain(synth_prompt)

    if simple:
        eli5_prompt = (
            "Rewrite this summary in *very simple beginner-level terms*:\n\n"
            f"{final_summary}"
        )
        simple_version = ask_brain(eli5_prompt)
        return f"{final_summary}\n\n---\n\nSimple explanation:\n{simple_version}"

    return final_summary


#  KNOWLEDGE BASE (RAG MEMORY)

def index_pdf_bytes_to_kb(pdf_bytes: bytes, source_name: str = "uploaded"):
    """Extract text, chunk it, and store into local knowledge base."""
    fp = io.BytesIO(pdf_bytes)
    reader = PdfReader(fp)

    new_chunks = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if not text.strip():
            continue

        chunks = split_text_to_chunks(text, chunk_size=800, overlap=100)

        for j, c in enumerate(chunks):
            new_chunks.append({
                "text": c,
                "source": f"{source_name} | page {i+1}, chunk {j+1}"
            })

    if new_chunks:
        add_texts_to_index(new_chunks)

    return len(new_chunks)


def ask_with_context(question: str, top_k: int = 3) -> str:
    """RAG querying: retrieve top-k notes and answer using them."""
    results = query_kb(question, top_k=top_k)

    if not results:
        answer = ask_brain(question)
        return answer + "\n\n(Sources: none)"

    context_parts = []
    sources = []

    for score, meta in results:
        context_parts.append(meta["text"][:900])  # truncate context
        sources.append(meta["source"])

    context = "\n\n---\n\n".join(context_parts)

    prompt = (
        "Use ONLY the notes below to answer the question.\n"
        "If answer is not found in the notes, say: 'Not found in notes.'\n\n"
        f"NOTES:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Give a clear answer, then list which sources you used."
    )

    answer = ask_brain(prompt)
    return f"{answer}\n\nSources used: {', '.join(sources)}"

