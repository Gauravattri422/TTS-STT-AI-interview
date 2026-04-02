"""Configuration module for API keys and settings"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MURF_API_KEY = os.getenv("MURF_API_KEY")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    
    # File Upload
    UPLOAD_DIR = "uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    
    # API Endpoints
    GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
    MURF_ENDPOINT = "https://api.murf.ai/v1/speech/stream"
    DEEPGRAM_ENDPOINT = "https://api.deepgram.com/v1/listen"
    
    # Models
    GROQ_QUESTION_MODEL = "llama-3.3-70b-versatile"
    GROQ_EVAL_MODEL = "llama-3.1-8b-instant"
    DEEPGRAM_MODEL = "nova-2"
    
    # Server
    HOST = "0.0.0.0"
    PORT = 8080

# Create upload directory
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
