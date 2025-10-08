# backend/app/main.py
# FastAPI app implementing required endpoints.

import os
import uuid
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import shutil
from fastapi.middleware.cors import CORSMiddleware

from .db import SessionLocal, engine, Base
from . import models, schemas, ml_utils

# create tables (simple for class demo)
Base.metadata.create_all(bind=engine)

# ✅ Create app once
app = FastAPI(title="ML Resume Screening (Demo)")

# ✅ Enable CORS (must come after app creation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # or ["http://localhost:5173"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===========================
# ✅ ROUTES START HERE
# ===========================

# POST /api/resumes/upload
@app.post("/api/resumes/upload", response_model=schemas.ResumeUploadResponse)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # save upload
    ext = os.path.splitext(file.filename)[1].lower()
    uid = str(uuid.uuid4())[:8]
    raw_name = f"{uid}_{file.filename}"
    saved_path = os.path.join(UPLOAD_DIR, raw_name)

    # Save to disk
    with open(saved_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    # convert if .doc
    if ext == ".doc":
        converted = ml_utils.convert_doc_to_docx(saved_path)
        if os.path.exists(converted):
            saved_path = converted

    # extract text
    try:
        text = ml_utils.extract_text_docx(saved_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}")

    parsed = ml_utils.parse_contacts(text)

    # load canonical skills from DB
    skills_rows = db.query(models.Skill).all()
    canonical_skills = [s.skill_name for s in skills_rows]

    # extract skills
    detected_skills = ml_utils.extract_skills(text, canonical_skills, threshold=0.72)

    # upsert candidate
    candidate = None
    if parsed.get("email"):
        candidate = db.query(models.Candidate).filter_by(email=parsed["email"]).first()
    if not candidate:
        candidate = models.Candidate(full_name=parsed.get("name"), email=parsed.get("email"), phone=parsed.get("phone"))
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    # create resume entry
    resume = models.Resume(
        candidate_id=candidate.candidate_id,
        filename=os.path.basename(saved_path),
        upload_path=os.path.abspath(saved_path),
        raw_text=text,
        parsed_json={"parsed": parsed, "skills": detected_skills}
    )

    # compute embedding
    try:
        emb = ml_utils.embed_text(text)
        resume.embedding = emb
    except Exception:
        resume.embedding = None

    db.add(resume)
    db.commit()
    db.refresh(resume)

    # insert resume_skills
    for skill_name, confidence in detected_skills:
        s_row = db.query(models.Skill).filter_by(skill_name=skill_name).first()
        if s_row:
            rs = models.ResumeSkill(resume_id=resume.resume_id, skill_id=s_row.skill_id, confidence=confidence)
            db.add(rs)
    db.commit()

    return {
        "resume_id": resume.resume_id,
        "candidate_id": candidate.candidate_id,
        "parsed": {
            "name": parsed.get("name"),
            "email": parsed.get("email"),
            "phone": parsed.get("phone"),
            "skills": detected_skills
        }
    }

# ===========================
# Other endpoints (unchanged)
# ===========================

@app.get("/api/candidates", response_model=List[schemas.CandidateOut])
def list_candidates(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    rows = db.query(models.Candidate).order_by(models.Candidate.created_at.desc()).offset(offset).limit(limit).all()
    return [{"candidate_id": r.candidate_id, "full_name": r.full_name, "email": r.email, "phone": r.phone} for r in rows]

@app.get("/api/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    cand = db.query(models.Candidate).filter_by(candidate_id=candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    resumes = db.query(models.Resume).filter_by(candidate_id=candidate_id).all()
    res_data = []
    for r in resumes:
        res_data.append({
            "resume_id": r.resume_id,
            "filename": r.filename,
            "uploaded_at": r.uploaded_at,
            "parsed_json": r.parsed_json
        })
    return {"candidate": {"candidate_id": cand.candidate_id, "full_name": cand.full_name, "email": cand.email, "phone": cand.phone}, "resumes": res_data}

@app.get("/api/resumes/{resume_id}/download")
def download_resume(resume_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Resume).filter_by(resume_id=resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    return FileResponse(r.upload_path, filename=r.filename)

@app.post("/api/jobs", response_model=schemas.JobOut)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    job_row = models.Job(title=job.title, description=job.description)
    try:
        emb = ml_utils.embed_text(job.description or job.title)
        job_row.embedding = emb
    except Exception:
        job_row.embedding = None
    db.add(job_row)
    db.commit()
    db.refresh(job_row)

    for s in job.skills or []:
        s = s.strip()
        if not s: continue
        skill_row = db.query(models.Skill).filter_by(skill_name=s).first()
        if not skill_row:
            skill_row = models.Skill(skill_name=s, canonical_name=s.title())
            db.add(skill_row)
            db.commit()
            db.refresh(skill_row)
        js = models.JobSkill(job_id=job_row.job_id, skill_id=skill_row.skill_id, required_level=1)
        db.add(js)
    db.commit()
    return {"job_id": job_row.job_id, "title": job_row.title, "description": job_row.description}

@app.post("/api/jobs/{job_id}/rank")
def rank_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_skill_links = db.query(models.JobSkill).filter_by(job_id=job_id).all()
    job_skill_ids = [jl.skill_id for jl in job_skill_links]

    resumes = db.query(models.Resume).all()
    db.query(models.Ranking).filter_by(job_id=job_id).delete()
    db.commit()

    for r in resumes:
        if not r.embedding or not job.embedding:
            continue
        r_skill_links = db.query(models.ResumeSkill).filter_by(resume_id=r.resume_id).all()
        r_skill_ids = [rl.skill_id for rl in r_skill_links]
        scores = ml_utils.compute_final_score(job.embedding, r.embedding, job_skill_ids, r_skill_ids, weight_semantic=0.7, weight_skill=0.3)
        rank = models.Ranking(job_id=job_id, resume_id=r.resume_id, score=scores["final_score"])
        db.add(rank)
    db.commit()
    return {"status": "done", "ranked": db.query(models.Ranking).filter_by(job_id=job_id).count()}

@app.get("/api/jobs/{job_id}/rankings")
def get_rankings(job_id: int, db: Session = Depends(get_db)):
    rows = db.query(models.Ranking).filter_by(job_id=job_id).order_by(models.Ranking.score.desc()).all()
    out = []
    for row in rows:
        resume = db.query(models.Resume).filter_by(resume_id=row.resume_id).first()
        candidate = db.query(models.Candidate).filter_by(candidate_id=resume.candidate_id).first()
        out.append({
            "ranking_id": row.ranking_id,
            "resume_id": resume.resume_id,
            "candidate_id": candidate.candidate_id,
            "candidate_name": candidate.full_name,
            "score": row.score
        })
    return out

@app.get("/api/analytics/top-skills")
def top_skills(limit: int = 10, db: Session = Depends(get_db)):
    from sqlalchemy import func
    agg = db.query(models.Skill.skill_id, models.Skill.skill_name, func.count(models.ResumeSkill.id).label("matches")) \
            .join(models.ResumeSkill, models.ResumeSkill.skill_id == models.Skill.skill_id) \
            .group_by(models.Skill.skill_id, models.Skill.skill_name) \
            .order_by(func.count(models.ResumeSkill.id).desc()) \
            .limit(limit).all()
    return [{"skill_id": a.skill_id, "skill_name": a.skill_name, "matches": a.matches} for a in agg]
