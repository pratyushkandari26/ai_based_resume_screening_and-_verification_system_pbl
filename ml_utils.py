# backend/app/ml_utils.py
# Utilities: doc conversion, extraction, parsing, embeddings, similarity, scoring.

import os
import re
import uuid
import subprocess
from typing import List, Tuple, Dict
from docx import Document
import numpy as np
from sentence_transformers import SentenceTransformer

# Lazy-loaded model singleton
_MODEL = None

def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL

def safe_save_upload(upload_file, dest_path):
    # Save UploadFile to disk
    with open(dest_path, "wb") as buffer:
        # upload_file.file is a SpooledTemporaryFile/IO
        chunk = upload_file.file.read()
        buffer.write(chunk)
    return dest_path

def convert_doc_to_docx(doc_path: str) -> str:
    """
    Convert .doc -> .docx using libreoffice command-line.
    Requires libreoffice installed.
    Returns new .docx path (same directory).
    """
    out_dir = os.path.dirname(doc_path) or "."
    # call libreoffice safely
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "docx",
        "--outdir", out_dir, doc_path
    ], check=False)  # don't fail hard; in class demo, document may already be docx
    base = os.path.splitext(os.path.basename(doc_path))[0]
    new_path = os.path.join(out_dir, f"{base}.docx")
    return new_path

def extract_text_docx(path: str) -> str:
    """Read .docx file and return concatenated text."""
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs)

# Contact regexes (simple, general)
_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
_PHONE_RE = re.compile(r"(\+?\d{1,3}[\s\-\.\(]?)?(\d{2,4}[\s\-\.\)]?){2,4}")

def parse_contacts(text: str) -> Dict:
    email_match = _EMAIL_RE.search(text)
    email = email_match.group(0) if email_match else None
    phone_match = _PHONE_RE.search(text)
    phone = phone_match.group(0) if phone_match else None
    # Heuristic for name: first non-empty line not containing email/phone
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = None
    for line in lines[:5]:
        if email and email in line: continue
        if phone and phone in line: continue
        # simple garbage filter
        if len(line.split()) <= 6 and len(line) < 60:
            name = line
            break
    return {"name": name, "email": email, "phone": phone}

def extract_skills(text: str, canonical_skills: List[str], threshold: float = 0.72) -> List[Tuple[str, float]]:
    """
    Return list of (skill_name, confidence).
    - exact substring matches (high confidence)
    - embedding similarity fallback (if model available)
    """
    found = {}
    low = text.lower()
    # exact matches
    for s in canonical_skills:
        if s.lower() in low:
            found[s] = max(found.get(s, 0.7), 0.9)  # exact match high confidence

    # embedding-based augmentation
    model = None
    try:
        model = get_model()
    except Exception:
        model = None

    if model:
        # embed resume text once
        resume_emb = model.encode(text, convert_to_numpy=True)
        skill_embs = model.encode(canonical_skills, convert_to_numpy=True)
        # compute cosine sims
        for i, s in enumerate(canonical_skills):
            sim = float(np.dot(resume_emb, skill_embs[i]) / (np.linalg.norm(resume_emb)+1e-8) / (np.linalg.norm(skill_embs[i])+1e-8))
            if sim >= threshold:
                found[s] = max(found.get(s, 0.5), sim)  # use sim as confidence
    # return list
    return [(k, float(v)) for k, v in found.items()]

def embed_text(text: str) -> List[float]:
    model = get_model()
    vec = model.encode(text, convert_to_numpy=True)
    return vec.tolist()

def cosine_scaled(a: List[float], b: List[float]) -> float:
    # Return cosine similarity scaled to [0,1]
    a = np.array(a)
    b = np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-10
    cos = float(np.dot(a, b) / denom)
    return (cos + 1.0) / 2.0  # scale from [-1,1] to [0,1]

def compute_final_score(job_emb, resume_emb, job_skill_ids, resume_skill_ids, weight_semantic=0.7, weight_skill=0.3):
    # semantic
    s_sem = cosine_scaled(job_emb, resume_emb)
    # skill score: matched_required_skills / total_required_skills
    total = len(job_skill_ids)
    if total == 0:
        s_skill = 1.0  # if job requires no skills, treat as perfect on skills
    else:
        matched = len(set(job_skill_ids).intersection(set(resume_skill_ids)))
        s_skill = matched / total
    final = weight_semantic * s_sem + weight_skill * s_skill
    return {"score_semantic": s_sem, "score_skill": s_skill, "final_score": final}
