import re
import textwrap
from pathlib import Path
import streamlit as st

def preprocess_input(text: str) -> dict:
    """Analyze input text and extract key components."""
    if not text or not text.strip():
        return {"word_count": 0, "complexity": "none"}
    
    return {
        "word_count": len(text.split()),
        "has_conditions": bool(re.search(r'\b(if|when|while|until|greater|less|equal|above|below)\b', text.lower())),
        "has_actions": bool(re.search(r'\b(turn|start|stop|enable|disable|activate|deactivate|open|close)\b', text.lower())),
        "has_sensors": bool(re.search(r'\b(temperature|pressure|level|flow|sensor|input|feedback)\b', text.lower())),
        "has_actuators": bool(re.search(r'\b(motor|pump|valve|heater|output|actuator|drive)\b', text.lower())),
        "has_safety": bool(re.search(r'\b(emergency|stop|safety|interlock|fail|alarm)\b', text.lower())),
        "complexity": "high" if len(text.split()) > 50 else "medium" if len(text.split()) > 20 else "low"
    }

def validate_plc_requirements(text: str) -> dict:
    """Validate and categorize PLC requirements."""
    validation = {
        "is_valid": True,
        "warnings": [],
        "suggestions": [],
        "confidence": 0.0
    }
    
    if len(text.strip()) < 10:
        validation["is_valid"] = False
        validation["warnings"].append("Input too short for meaningful PLC logic")
        return validation
    
    safety_keywords = ["emergency", "stop", "safety", "interlock", "fail"]
    if not any(keyword in text.lower() for keyword in safety_keywords):
        validation["suggestions"].append("Consider adding safety interlocks")
    
    plc_terms = ["input", "output", "timer", "counter", "analog", "digital", "sensor", "actuator", "motor", "valve", "temperature", "pressure"]
    found_terms = sum(1 for term in plc_terms if term in text.lower())
    validation["confidence"] = min(found_terms / 5, 1.0) 
    
    return validation


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


def extract_first_code_block(text: str) -> str | None:
    """Extract the first code block from markdown text."""
    if not text:
        return None
    m = re.search(r"``````", text, flags=re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def safe_agent_run(agent, prompt, operation_name="operation"):
    """Safely run an agent with error handling and retries."""
    import streamlit as st
    for attempt in range(3):
        try:
            response = agent.run(prompt)
            return getattr(response, "content", str(response))
        except Exception as e:
            if attempt < 2:
                st.warning(f"{operation_name} attempt {attempt + 1} failed, retrying...")
                continue
            else:
                st.error(f"{operation_name} failed after 3 attempts: {str(e)}")
                return f"Error in {operation_name}: {str(e)}"
