from pydantic import BaseModel
from typing import Optional, List

class QuestionRequest(BaseModel):
    skills: List[str]
    hobbies: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    experience: Optional[str] = ""

class TTSRequest(BaseModel):
    text: str

class EvaluationRequest(BaseModel):
    question: str
    answer: str
    difficulty: str

class ResumeData(BaseModel):
    skills: List[str]
    certifications: List[str]
    hobbies: List[str]
    experience: str
