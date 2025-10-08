# backend/app/models.py
# SQLAlchemy ORM models that mirror the SQL CREATE TABLE statements above.

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class HRUser(Base):
    __tablename__ = "hr_users"
    hr_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="hr")

class Candidate(Base):
    __tablename__ = "candidates"
    candidate_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(Text)
    email = Column(Text, unique=True)
    phone = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="candidate")

class Resume(Base):
    __tablename__ = "resumes"
    resume_id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id", ondelete="CASCADE"))
    filename = Column(Text)
    upload_path = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text)
    parsed_json = Column(JSONB)
    embedding = Column(JSONB)

    candidate = relationship("Candidate", back_populates="resumes")
    resume_skills = relationship("ResumeSkill", back_populates="resume")
    rankings = relationship("Ranking", back_populates="resume")

class Skill(Base):
    __tablename__ = "skills"
    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(Text, unique=True, nullable=False)
    canonical_name = Column(Text)

    resume_links = relationship("ResumeSkill", back_populates="skill")
    job_links = relationship("JobSkill", back_populates="skill")

class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    confidence = Column(Float)

    resume = relationship("Resume", back_populates="resume_skills")
    skill = relationship("Skill", back_populates="resume_links")

class Job(Base):
    __tablename__ = "jobs"
    job_id = Column(Integer, primary_key=True, index=True)
    hr_id = Column(Integer, ForeignKey("hr_users.hr_id"))
    title = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(JSONB)

    hr = relationship("HRUser", back_populates="jobs")
    job_skills = relationship("JobSkill", back_populates="job")
    rankings = relationship("Ranking", back_populates="job")

class JobSkill(Base):
    __tablename__ = "job_skills"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    required_level = Column(Integer, default=1)

    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill", back_populates="job_links")

class Ranking(Base):
    __tablename__ = "rankings"
    ranking_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"))
    resume_id = Column(Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"))
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="rankings")
    resume = relationship("Resume", back_populates="rankings")
