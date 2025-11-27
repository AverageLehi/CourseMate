import os
import json
import requests
from typing import List, Optional

# Simple offline AI service using Ollama (http://localhost:11434)
# Configure model via env var OLLAMA_MODEL (default: 'llama3')

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

class AIServiceError(Exception):
    pass

def _ollama_generate(prompt: str, temperature: float = 0.2, system: Optional[str] = None) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 512,  # Limit output tokens for faster response
        }
    }
    if system:
        payload["system"] = system
    try:
        r = requests.post(url, json=payload, timeout=180)  # Increased timeout for model inference
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")
    except requests.Timeout:
        raise AIServiceError("Ollama request timed out - model may be slow or overloaded")
    except requests.RequestException as e:
        raise AIServiceError(f"Ollama request failed: {e}")
    except json.JSONDecodeError:
        raise AIServiceError("Invalid response from Ollama")

def list_models() -> List[str]:
    """Return a list of available local Ollama model names (best-effort)."""
    try:
        url = f"{OLLAMA_HOST}/api/tags"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        models = []
        # Newer Ollama returns {"models": [{"name": "llama3"}, ...]}
        for m in data.get("models", []):
            name = m.get("name")
            if name:
                models.append(name)
        return models
    except Exception:
        return []

def set_model(model_name: str):
    """Set the active model for subsequent generations."""
    global OLLAMA_MODEL
    model_name = (model_name or "").strip()
    if model_name:
        OLLAMA_MODEL = model_name

# Public API

def summarize(text: str) -> str:
    if not text or not text.strip():
        return "No content to summarize."
    system = (
        "You are a helpful study assistant. Summarize the text into: "
        "1) Key points (bulleted) 2) Concepts 3) Action items if any. Keep it concise."
    )
    prompt = f"Summarize the following note:\n\n{text}\n\nProvide structured output."
    return _ollama_generate(prompt, temperature=0.2, system=system)


def generate_template(kind: str, prompt_text: str) -> str:
    kind = (kind or "study").lower()
    if kind not in ("study", "planner"):
        kind = "study"
    if kind == "study":
        system = (
            "You design study note templates. Output a plain text template that includes sections "
            "like Topic, Key Points, Examples, and Summary. Use bullets where helpful."
        )
        user_prompt = (
            f"Create a study template tailored to: '{prompt_text}'. "
            "Only output the template structure, no commentary."
        )
    else:
        system = (
            "You design planner templates. Output a plain text template that includes Date, Priorities, "
            "Schedule (time blocks) and Tasks with [ ] checkboxes, and Notes."
        )
        user_prompt = (
            f"Create a planner template tailored to: '{prompt_text}'. "
            "Only output the template structure, no commentary."
        )
    return _ollama_generate(user_prompt, temperature=0.3, system=system)


def extract_tags(text: str) -> List[str]:
    if not text or not text.strip():
        return []
    system = (
        "Extract concise hashtags from the text. Return a comma-separated list of tokens like #math, #algebra. "
        "Avoid duplicates, keep 3-8 most relevant."
    )
    resp = _ollama_generate(f"Extract hashtags from:\n\n{text}\n\nReturn only the list.", temperature=0.2, system=system)
    # Parse simple comma-separated output into list of #tokens
    parts = [p.strip() for p in resp.replace("\n", ",").split(",")]
    tags = []
    seen = set()
    for p in parts:
        if not p:
            continue
        token = p
        if not token.startswith('#'):
            token = '#' + token.lstrip('#').replace(' ', '-')
        t = token.strip()
        if t and t not in seen:
            seen.add(t)
            tags.append(t)
    return tags


def answer_question(context: str, question: str) -> str:
    if not question or not question.strip():
        return "Please enter a question."
    system = (
        "You are a helpful assistant answering questions using the provided context. "
        "Cite relevant parts briefly and be concise."
    )
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    return _ollama_generate(prompt, temperature=0.3, system=system)
