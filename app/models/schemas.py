"""Pydantic models for request/response validation"""
from pydantic import BaseModel
from typing import Optional, List

class QuestionRequest(BaseModel):
    """Request model for generating questions"""
    skills: List[str]
    hobbies: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    experience: Optional[str] = ""

class TTSRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str

class EvaluationRequest(BaseModel):
    """Request model for answer evaluation"""
    question: str
    answer: str
    difficulty: str

class ResumeData(BaseModel):
    """Resume parsed data"""
    skills: List[str]
    certifications: List[str]
    hobbies: List[str]
    experience: str
