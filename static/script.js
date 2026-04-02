// Global variables
let sessionId = null;
let questions = [];
let currentQuestionIndex = 0;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentAnswer = "";
let evaluations = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupFileUpload();
});

// File upload setup
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeFile');

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9ff';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = '';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// Handle file upload
async function handleFileUpload(file) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = '<div class="loading"></div> Uploading and parsing resume...';
    statusDiv.className = 'status-message info';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:8080/api/upload-resume', {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Upload failed: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        sessionId = data.session_id;
        
        statusDiv.innerHTML = '✓ Resume uploaded successfully!';
        statusDiv.className = 'status-message success';

        // Display resume info
        displayResumeInfo(data.resume_data);

        // Switch to resume info section
        setTimeout(() => {
            showSection('resumeInfoSection');
        }, 1000);

    } catch (error) {
        statusDiv.innerHTML = `✗ Error: ${error.message}. Please try again.`;
        statusDiv.className = 'status-message error';
        console.error('Upload error:', error);
    }
}

// Display resume information
function displayResumeInfo(data) {
    const infoDiv = document.getElementById('resumeInfo');
    
    let html = '';
    
    if (data.skills && data.skills.length > 0) {
        html += `
            <div class="info-section">
                <h3>Skills</h3>
                <ul>
                    ${data.skills.map(skill => `<li>${skill}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (data.certifications && data.certifications.length > 0) {
        html += `
            <div class="info-section">
                <h3>Certifications</h3>
                <ul>
                    ${data.certifications.map(cert => `<li>${cert}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (data.hobbies && data.hobbies.length > 0) {
        html += `
            <div class="info-section">
                <h3>Hobbies & Interests</h3>
                <ul>
                    ${data.hobbies.map(hobby => `<li>${hobby}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (data.experience) {
        html += `
            <div class="info-section">
                <h3>Experience</h3>
                <p>${data.experience}</p>
            </div>
        `;
    }
    
    infoDiv.innerHTML = html;
}

// Start interview
async function startInterview() {
    const resumeData = JSON.parse(localStorage.getItem('resumeData') || '{}');
    const infoDiv = document.getElementById('resumeInfo');
    
    // Extract data from displayed info
    const skills = Array.from(infoDiv.querySelectorAll('.info-section:first-child li'))
        .map(li => li.textContent.trim());
    
    showMessage('Generating interview questions based on your profile...', 'system');
    showSection('interviewSection');

    try {
        // Generate questions
        const response = await fetch('http://localhost:8080/api/generate-questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                skills: skills.length > 0 ? skills : ['Python', 'JavaScript'],
                hobbies: [],
                certifications: [],
                experience: ''
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate questions');
        }

        const data = await response.json();
        questions = data.questions;

        // Start first question
        setTimeout(() => {
            askQuestion(0);
        }, 1500);

    } catch (error) {
        showMessage('Error generating questions. Please try again.', 'system');
        console.error('Question generation error:', error);
    }
}

// Ask a question
async function askQuestion(index) {
    if (index >= questions.length) {
        finishInterview();
        return;
    }

    currentQuestionIndex = index;
    const question = questions[index];

    // Update progress
    document.getElementById('questionNumber').textContent = `Question ${index + 1} of ${questions.length}`;
    document.getElementById('progressFill').style.width = `${((index + 1) / questions.length) * 100}%`;

    // Display question
    showMessage(question.question, 'system', question.difficulty);

    // Hide controls during question playback
    document.getElementById('recordBtn').style.display = 'none';
    document.getElementById('nextBtn').style.display = 'none';
    document.getElementById('transcriptArea').style.display = 'none';

    // Convert to speech and play
    await playQuestionAudio(question.question);

    // Automatically start recording after question is spoken
    showMessage('Recording started. Speak your answer, then click "Stop Recording" when done.', 'system');
    await startRecording();
}

// Play question audio
async function playQuestionAudio(text) {
    try {
        const response = await fetch('http://localhost:8080/api/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });

        if (!response.ok) {
            throw new Error('TTS failed');
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = document.getElementById('questionAudio');
        audio.src = audioUrl;
        
        return new Promise((resolve) => {
            audio.onended = resolve;
            audio.play();
        });

    } catch (error) {
        console.error('TTS error:', error);
        // Continue anyway
    }
}

// Toggle recording (now only stops since auto-start)
async function toggleRecording() {
    if (isRecording) {
        await stopRecording();
    }
}

// Start recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await transcribeAudio(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;

        // Update UI - Show stop button
        document.getElementById('recordBtn').style.display = 'flex';
        document.getElementById('recordBtn').classList.add('recording');
        document.getElementById('recordText').textContent = 'Stop Recording';
        document.getElementById('recordingIndicator').classList.add('active');

    } catch (error) {
        console.error('Microphone error:', error);
        alert('Could not access microphone. Please check permissions.');
    }
}

// Stop recording
async function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;

        // Update UI
        document.getElementById('recordBtn').classList.remove('recording');
        document.getElementById('recordBtn').style.display = 'none';
        document.getElementById('recordText').innerHTML = '<div class="loading"></div> Processing...';
        document.getElementById('recordingIndicator').classList.remove('active');
    }
}

// Transcribe audio
async function transcribeAudio(audioBlob) {
    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        const response = await fetch('http://localhost:8080/api/speech-to-text', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('STT failed');
        }

        const data = await response.json();
        currentAnswer = data.transcript;

        // Display transcript
        document.getElementById('transcriptText').textContent = currentAnswer;
        document.getElementById('transcriptArea').style.display = 'block';

        // Show user message
        showMessage(currentAnswer, 'user');

        // Store answer (no immediate evaluation)
        evaluations.push({
            question: questions[currentQuestionIndex].question,
            answer: currentAnswer,
            difficulty: questions[currentQuestionIndex].difficulty,
            evaluation: null  // Will be filled at the end
        });

        // Show acknowledgment
        showMessage('Thank you for your answer. Moving to the next question...', 'system');

        // Automatically move to next question after 2 seconds
        setTimeout(async () => {
            await nextQuestion();
        }, 2000);

    } catch (error) {
        console.error('STT error:', error);
        alert('Error transcribing audio. Please try again.');
        document.getElementById('recordText').textContent = 'Stop Recording';
        document.getElementById('recordBtn').style.display = 'flex';
        document.getElementById('recordBtn').classList.remove('recording');
        // Restart recording
        await startRecording();
    }
}

// Evaluate all answers at the end
async function evaluateAllAnswers() {
    showMessage('Evaluating all your answers, please wait...', 'system');
    
    for (let i = 0; i < evaluations.length; i++) {
        const item = evaluations[i];
        
        try {
            const response = await fetch('http://localhost:8080/api/evaluate-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: item.question,
                    answer: item.answer,
                    difficulty: item.difficulty
                })
            });

            if (!response.ok) {
                throw new Error('Evaluation failed');
            }

            const evaluation = await response.json();
            evaluations[i].evaluation = evaluation;

        } catch (error) {
            console.error('Evaluation error:', error);
            evaluations[i].evaluation = {
                score: 5,
                feedback: 'Could not evaluate this answer.',
                strengths: 'Answer recorded.',
                improvements: 'N/A'
            };
        }
    }
}

// Next question
async function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        askQuestion(currentQuestionIndex);
    } else {
        await finishInterview();
    }
}

// Finish interview
async function finishInterview() {
    // Evaluate all answers first
    await evaluateAllAnswers();
    
    showSection('resultsSection');
    displayResults();
}

// Display results
function displayResults() {
    const resultsDiv = document.getElementById('resultsContent');
    
    let totalScore = 0;
    let html = '';

    evaluations.forEach((item, index) => {
        totalScore += item.evaluation.score;
        html += `
            <div class="result-card">
                <h3>Question ${index + 1}</h3>
                <p><strong>Q:</strong> ${item.question}</p>
                <p><strong>Your Answer:</strong> ${item.answer}</p>
                <div class="score">Score: ${item.evaluation.score}/10</div>
                <p><strong>Feedback:</strong> ${item.evaluation.feedback}</p>
                <p><strong>Strengths:</strong> ${item.evaluation.strengths}</p>
                <p><strong>Improvements:</strong> ${item.evaluation.improvements}</p>
            </div>
        `;
    });

    const averageScore = (totalScore / evaluations.length).toFixed(1);
    
    html = `
        <div class="result-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none;">
            <h3 style="color: white;">Overall Performance</h3>
            <div class="score" style="color: white; font-size: 3em;">${averageScore}/10</div>
            <p>You completed ${evaluations.length} questions</p>
        </div>
    ` + html;

    resultsDiv.innerHTML = html;
}

// Show message in conversation
function showMessage(text, type, badge = '') {
    const conversationArea = document.getElementById('conversationArea');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const label = type === 'system' ? 'AI Interviewer' : 'You';
    const badgeHtml = badge ? ` <span style="background: rgba(255,255,255,0.3); padding: 3px 10px; border-radius: 12px; font-size: 0.85em;">${badge}</span>` : '';
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>${label}${badgeHtml}</strong>
            <p>${text}</p>
        </div>
    `;
    
    conversationArea.appendChild(messageDiv);
    conversationArea.scrollTop = conversationArea.scrollHeight;
}

// Show section
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}
