# backend/app/schemas.py
# Pydantic schemas for request/response validation

from pydantic import BaseModel
from typing import List, Optional, Any

class ResumeUploadResponse(BaseModel):
    resume_id: int
    candidate_id: int
    parsed: dict

class CandidateOut(BaseModel):
    candidate_id: int
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]

class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    skills: Optional[List[str]] = []

class JobOut(BaseModel):
    job_id: int
    title: str
    description: Optional[str] = None

class RankingOut(BaseModel):
    ranking_id: int
    resume_id: int
    candidate_id: int
    candidate_name: Optional[str]
    score: float
