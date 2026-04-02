"""Text-to-Speech service using MURF AI and gTTS"""
import httpx
import io
import base64
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
from app.config import Config

class TTSService:
    """Service for text-to-speech conversion"""
    
    @staticmethod
    async def generate_speech(text: str) -> StreamingResponse:
        """Convert text to speech audio"""
        print(f"TTS Request: {text[:100]}...")
        
        # Try MURF AI first
        try:
            return await TTSService._murf_ai_tts(text)
        except Exception as murf_error:
            print(f"MURF AI error: {murf_error}, falling back to gTTS")
        
        # Fallback to gTTS
        try:
            return TTSService._gtts_fallback(text)
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
    
    @staticmethod
    async def _murf_ai_tts(text: str) -> StreamingResponse:
        """Generate speech using MURF AI"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                Config.MURF_ENDPOINT,
                headers={
                    "api-key": Config.MURF_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "voiceId": "Matthew",
                    "model": "FALCON",
                    "multiNativeLocale": "en-US"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"MURF Response: {result}")
                
                if 'audioContent' in result:
                    audio_data = base64.b64decode(result['audioContent'])
                    return StreamingResponse(
                        io.BytesIO(audio_data),
                        media_type="audio/mpeg",
                        headers={"Content-Disposition": "inline; filename=speech.mp3"}
                    )
                elif 'audioFile' in result:
                    audio_url = result['audioFile']
                    audio_response = await client.get(audio_url)
                    return StreamingResponse(
                        io.BytesIO(audio_response.content),
                        media_type="audio/mpeg",
                        headers={"Content-Disposition": "inline; filename=speech.mp3"}
                    )
                else:
                    raise Exception(f"MURF API returned unexpected format: {result}")
            else:
                raise Exception(f"MURF API Error: {response.status_code} - {response.text}")
    
    @staticmethod
    def _gtts_fallback(text: str) -> StreamingResponse:
        """Generate speech using Google TTS (fallback)"""
        print("Using gTTS fallback...")
        tts = gTTS(text=text, lang='en', slow=False)
        
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        print("TTS generation successful with gTTS")
        
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )
