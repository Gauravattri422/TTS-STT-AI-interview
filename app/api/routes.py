from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import QuestionRequest, TTSRequest, EvaluationRequest
from app.services import GroqService, TTSService, STTService, ResumeParser
from app.config import Config
import os

router = APIRouter()

# Store interview sessions
interview_sessions = {}


@router.get("/")
async def root():
    """Serve the main page"""
    return FileResponse("static/index.html")


@router.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume"""
    try:
        # Save uploaded file
        file_path = os.path.join(Config.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse resume based on file type
        if file.filename.endswith('.pdf'):
            resume_data = ResumeParser.parse_pdf(file_path)
        elif file.filename.endswith('.docx'):
            resume_data = ResumeParser.parse_docx(file_path)
        elif file.filename.endswith('.txt'):
            resume_data = ResumeParser.parse_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Generate session ID
        session_id = str(hash(file.filename + str(len(interview_sessions))))
        interview_sessions[session_id] = {"resume_data": resume_data}
        
        return {
            "session_id": session_id,
            "resume_data": resume_data,
            "message": "Resume uploaded and parsed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/generate-questions")
async def generate_questions(request: QuestionRequest):
    """Generate 5 interview questions using Groq API"""
    questions = await GroqService.generate_questions(
        skills=request.skills,
        hobbies=request.hobbies,
        certifications=request.certifications,
        experience=request.experience
    )
    return {"questions": questions}


@router.post("/api/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    return await TTSService.generate_speech(request.text)


@router.post("/api/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech to text using Deepgram"""
    audio_data = await audio.read()
    return await STTService.transcribe_audio(audio_data)


@router.post("/api/evaluate-answer")
async def evaluate_answer(request: EvaluationRequest):
    """Evaluate candidate's answer using Groq API"""
    return await GroqService.evaluate_answer(
        question=request.question,
        answer=request.answer,
        difficulty=request.difficulty
    )
