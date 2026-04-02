"""Speech-to-Text service using Deepgram"""
import httpx
from fastapi import HTTPException
from app.config import Config

class STTService:
    """Service for speech-to-text conversion"""
    
    @staticmethod
    async def transcribe_audio(audio_data: bytes) -> dict:
        """Transcribe audio to text using Deepgram"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{Config.DEEPGRAM_ENDPOINT}?model={Config.DEEPGRAM_MODEL}&smart_format=true",
                    headers={
                        "Authorization": f"Token {Config.DEEPGRAM_API_KEY}",
                        "Content-Type": "audio/wav"
                    },
                    content=audio_data
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=response.text)
                
                result = response.json()
                transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
                confidence = result['results']['channels'][0]['alternatives'][0]['confidence']
                
                return {
                    "transcript": transcript,
                    "confidence": confidence
                }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
