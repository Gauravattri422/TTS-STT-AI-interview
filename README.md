# AI Interview System - TTS & STT Powered

A comprehensive interview application that uses Text-to-Speech (TTS) and Speech-to-Text (STT) technologies to conduct interactive technical interviews.

## Features

✅ **Resume Upload & Parsing** - Extracts skills, hobbies, certifications from PDF/DOCX/TXT files
✅ **AI Question Generation** - Generates 5 questions (2 easy, 2 medium, 1 situation-based) using Groq LLM
✅ **Text-to-Speech** - AI interviewer speaks questions using MURF AI
✅ **Speech-to-Text** - Candidate responses transcribed using Deepgram
✅ **Real-time Evaluation** - Answers evaluated instantly with detailed feedback
✅ **Conversational Interface** - Dynamic, chat-like experience

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **APIs**:
  - Groq API (LLM for questions & evaluation)
  - MURF AI (Text-to-Speech)
  - Deepgram (Speech-to-Text)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

All API keys are already configured in `.env` file:
- Groq API Key
- MURF AI API Key
- Deepgram API Key

### 3. Run the Application

```bash
python main.py
```

The server will start at: `http://localhost:8080`

### 4. Access the Application

Open your browser and navigate to: `http://localhost:8080`

## Usage Flow

1. **Upload Resume** - Drag & drop or select your resume (PDF, DOCX, or TXT)
2. **Review Extracted Info** - Verify the skills, certifications, and hobbies extracted
3. **Start Interview** - Click "Start Interview" to begin
4. **Listen to Questions** - AI interviewer will read each question aloud
5. **Record Answers** - Click the record button and speak your answer
6. **View Transcripts** - Your spoken answers are transcribed in real-time
7. **Get Feedback** - Receive immediate evaluation after each answer
8. **Review Results** - See overall performance and detailed feedback

## Interview Structure

- **Question 1-2**: Easy, direct questions about basic concepts and skills
- **Question 3-4**: Medium difficulty with technical depth
- **Question 5**: Situation-based challenging scenario

## API Endpoints

### `POST /api/upload-resume`
Upload and parse resume file
- **Input**: File (PDF/DOCX/TXT)
- **Output**: Extracted resume data

### `POST /api/generate-questions`
Generate interview questions
- **Input**: Skills, certifications, hobbies
- **Output**: 5 interview questions

### `POST /api/text-to-speech`
Convert text to speech
- **Input**: Text string
- **Output**: Audio file (MP3)

### `POST /api/speech-to-text`
Transcribe audio to text
- **Input**: Audio file (WAV)
- **Output**: Transcribed text

### `POST /api/evaluate-answer`
Evaluate candidate's answer
- **Input**: Question, answer, difficulty
- **Output**: Score, feedback, strengths, improvements

## Project Structure

```
SST-TTS/
├── main.py                 # FastAPI backend
├── requirements.txt        # Python dependencies
├── .env                   # API keys (configured)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── static/               # Frontend files
│   ├── index.html       # Main HTML page
│   ├── styles.css       # Styling
│   └── script.js        # Frontend logic
└── uploads/             # Resume uploads (auto-created)
```

## Browser Requirements

- Modern browser with microphone access
- JavaScript enabled
- HTTPS or localhost (for microphone permissions)

## Notes

- Microphone permission required for audio recording
- Supports PDF, DOCX, and TXT resume formats
- Evaluation provides detailed feedback on each answer

## Troubleshooting

### Microphone not working
- Check browser permissions
- Ensure using HTTPS or localhost
- Try different browser (Chrome recommended)

### Resume parsing issues
- Ensure resume format is PDF, DOCX, or TXT
- Check if file is not corrupted
- Try converting to TXT if issues persist

### API errors
- Check internet connection
- Verify API keys in `.env` file
- Check API rate limits

## License

This project uses the following APIs with their respective terms of service:
- Groq API
- MURF AI
- Deepgram

---

Built with ❤️ using FastAPI, Groq, MURF AI, and Deepgram
