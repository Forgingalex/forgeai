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
    if not text or len(text) == 0:
        return []
    
    # Limit text size to prevent memory issues (10MB max)
    MAX_TEXT_SIZE = 10 * 1024 * 1024  # 10MB
    if len(text) > MAX_TEXT_SIZE:
        text = text[:MAX_TEXT_SIZE]
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    L = len(text)

    while start < L:
        end = min(start + chunk_size, L)
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        start = end - overlap
        if start >= L:
            break

    return chunks


#  PDF TEXT EXTRACTION

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using BytesIO + pypdf."""
    try:
        fp = io.BytesIO(pdf_bytes)
        reader = PdfReader(fp)
        texts = []
        
        # Limit number of pages to prevent memory issues
        MAX_PAGES = 100  # Process max 100 pages
        total_pages = len(reader.pages)
        pages_to_process = min(total_pages, MAX_PAGES)

        for i in range(pages_to_process):
            try:
                page = reader.pages[i]
                page_text = page.extract_text() or ""
                if page_text.strip():
                    texts.append(page_text)
            except Exception:
                # Skip problematic pages
                continue

        result = "\n\n".join(texts)
        
        # Truncate if still too large (5MB max)
        MAX_TEXT_SIZE = 5 * 1024 * 1024
        if len(result) > MAX_TEXT_SIZE:
            result = result[:MAX_TEXT_SIZE] + "\n\n[Text truncated due to size limits...]"
        
        return result

    except Exception:
        return ""


#  SUMMARIZATION ENGINE

def summarize_pdf(pdf_bytes: bytes, simple: bool = False) -> str:
    """Summarize PDF using page-by-page processing to avoid memory issues."""
    
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("utf-8")

    try:
        fp = io.BytesIO(pdf_bytes)
        reader = PdfReader(fp)
        
        # Limit pages for summarization
        MAX_PAGES_FOR_SUMMARY = 50  # Process max 50 pages for summary
        total_pages = len(reader.pages)
        pages_to_process = min(total_pages, MAX_PAGES_FOR_SUMMARY)
        
        if pages_to_process == 0:
            return "Could not extract text from this PDF. It may be scanned or unreadable."
        
        page_summaries = []
        
        # Process pages in batches to avoid memory issues
        for i in range(pages_to_process):
            try:
                page = reader.pages[i]
                page_text = page.extract_text() or ""
                
                if not page_text.strip():
                    continue
                
                # Limit page text size
                MAX_PAGE_TEXT = 5000  # Max 5000 chars per page
                if len(page_text) > MAX_PAGE_TEXT:
                    page_text = page_text[:MAX_PAGE_TEXT] + "..."
                
                # Summarize this page
                prompt = (
                    f"Summarize page {i+1} of {pages_to_process} in **2-3 bullet points**, each under 15 words.\n\n"
                    f"{page_text}"
                )
                try:
                    summary = ask_brain(prompt)
                    summary = "\n".join(summary.split("\n")[:3])
                    page_summaries.append(f"Page {i+1}: {summary}")
                except Exception:
                    # Skip if AI call fails
                    continue
                    
            except Exception:
                # Skip problematic pages
                continue
        
        if not page_summaries:
            return "Could not extract meaningful text from this PDF."
        
        combined = "\n".join(page_summaries)
        
        # Limit combined summary size
        MAX_COMBINED = 10000  # Max 10k chars
        if len(combined) > MAX_COMBINED:
            combined = combined[:MAX_COMBINED] + "\n\n[Summary truncated...]"
        
        # Final combined synthesis
        synth_prompt = (
            "Using the following page summaries, produce:\n"
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
        
    except MemoryError:
        return "PDF is too large to process. Please try a smaller file or split it into parts."
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


#  KNOWLEDGE BASE (RAG MEMORY)

def index_pdf_bytes_to_kb(pdf_bytes: bytes, source_name: str = "uploaded"):
    """Extract text, chunk it, and store into local knowledge base."""
    fp = io.BytesIO(pdf_bytes)
    reader = PdfReader(fp)

    new_chunks = []
    
    # Limit pages for indexing
    MAX_PAGES_FOR_INDEX = 200  # Max 200 pages
    total_pages = len(reader.pages)
    pages_to_process = min(total_pages, MAX_PAGES_FOR_INDEX)

    for i in range(pages_to_process):
        try:
            page = reader.pages[i]
            text = page.extract_text() or ""
            if not text.strip():
                continue

            # Limit page text size
            MAX_PAGE_TEXT = 10000  # Max 10k chars per page
            if len(text) > MAX_PAGE_TEXT:
                text = text[:MAX_PAGE_TEXT]

            chunks = split_text_to_chunks(text, chunk_size=800, overlap=100)

            for j, c in enumerate(chunks):
                new_chunks.append({
                    "text": c,
                    "source": f"{source_name} | page {i+1}, chunk {j+1}"
                })
        except Exception:
            # Skip problematic pages
            continue

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

