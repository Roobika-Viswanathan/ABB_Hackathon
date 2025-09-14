import re
from pathlib import Path
import streamlit as st

@st.cache_data
def load_kb() -> list[dict]:
    """Load knowledge base from files."""
    kb_dir = Path(__file__).parent / "kb"
    items: list[dict] = []
    
    if not kb_dir.exists():
        return items
    
    for p in kb_dir.rglob("*"):
        if p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                chunks = [c.strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
                for i, chunk in enumerate(chunks):
                    items.append({
                        "path": str(p.relative_to(kb_dir)),
                        "chunk_id": i,
                        "content": chunk
                    })
            except Exception:
                continue
    return items


def ensure_kb_loaded():
    """Ensure knowledge base is loaded in session state."""
    if st.session_state.kb_index is None:
        st.session_state.kb_index = load_kb()


def retrieve_kb(query: str, top_k: int = 4) -> list[dict]:
    """Retrieve relevant knowledge base items."""
    ensure_kb_loaded()
    if not st.session_state.kb_index:
        return []
    
    toks = re.findall(r"[a-zA-Z0-9_]+", query.lower())
    if not toks:
        return []
    
    scores = []
    for item in st.session_state.kb_index:
        content_l = item["content"].lower()
        score = sum(content_l.count(t) for t in toks)
        if score:
            scores.append((score, item))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scores[:top_k]]


def compose_rag_context(query: str, top_k: int = 4) -> str:
    """Compose RAG context from knowledge base."""
    hits = retrieve_kb(query, top_k)
    if not hits:
        return ""
    
    blocks = []
    for h in hits:
        header = f"Source: {h['path']}#{h['chunk_id']}"
        blocks.append(f"{header}\n{h['content']}")
    
    return "\n\n".join(blocks)
