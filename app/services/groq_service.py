"""Groq API service for question generation and evaluation"""
import httpx
import json
import re
from fastapi import HTTPException
from app.config import Config

class GroqService:
    """Service for interacting with Groq API"""
    
    @staticmethod
    async def generate_questions(skills: list, hobbies: list = None, certifications: list = None, experience: str = "") -> list:
        """Generate 5 interview questions based on candidate profile"""
        skills_str = ', '.join(skills[:5]) if skills else 'General Programming'
        
        print(f"Generating questions for skills: {skills_str}")
        
        context = f"""Generate exactly 5 technical interview questions for a candidate with these skills: {skills_str}

STRICT FORMAT - Return ONLY this JSON array, nothing else:
[
  {{"question": "What is Python and what are its key features?", "difficulty": "easy"}},
  {{"question": "Explain a project where you used {skills[0] if skills else 'programming'}", "difficulty": "easy"}},
  {{"question": "How would you optimize a slow database query?", "difficulty": "medium"}},
  {{"question": "Design a system to handle 1 million concurrent users", "difficulty": "medium"}},
  {{"question": "Tell me about a time when you had to debug a critical production issue under pressure", "difficulty": "hard"}}
]

Rules:
- Question 1-2: Easy, direct questions
- Question 3-4: Medium, technical depth
- Question 5: Situation-based scenario
- Return ONLY the JSON array"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    Config.GROQ_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": Config.GROQ_QUESTION_MODEL,
                        "messages": [
                            {"role": "system", "content": "You are a technical interviewer. Return ONLY valid JSON arrays, no markdown, no explanation."},
                            {"role": "user", "content": context}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1500
                    }
                )
                
                if response.status_code != 200:
                    print(f"Groq API Error: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=response.status_code, detail=f"Groq API error: {response.text}")
                
                result = response.json()
                questions_text = result['choices'][0]['message']['content']
                
                print(f"Groq Response: {questions_text[:200]}...")
                
                # Clean up response
                questions_text = questions_text.strip()
                questions_text = re.sub(r'^```json\s*', '', questions_text)
                questions_text = re.sub(r'^```\s*', '', questions_text)
                questions_text = re.sub(r'\s*```$', '', questions_text)
                questions_text = questions_text.strip()
                
                questions = json.loads(questions_text)
                
                # Validate
                if not isinstance(questions, list) or len(questions) != 5:
                    raise ValueError("Invalid question format")
                
                print(f"Successfully generated {len(questions)} questions")
                return questions
        
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {str(e)}")
            # Return fallback questions
            return GroqService._get_fallback_questions(skills)
        
        except Exception as e:
            print(f"Question Generation Error: {str(e)}")
            return GroqService._get_fallback_questions(skills)
    
    @staticmethod
    def _get_fallback_questions(skills: list) -> list:
        """Return fallback questions if API fails"""
        skill = skills[0] if skills else 'Python'
        return [
            {"question": f"What are the key features of {skill}?", "difficulty": "easy"},
            {"question": f"Can you describe a project where you used {skill}?", "difficulty": "easy"},
            {"question": "How do you approach debugging complex issues in production?", "difficulty": "medium"},
            {"question": "Design a scalable system architecture for a high-traffic web application", "difficulty": "medium"},
            {"question": "Tell me about a time when you had to make a critical technical decision under pressure", "difficulty": "hard"}
        ]
    
    @staticmethod
    async def evaluate_answer(question: str, answer: str, difficulty: str) -> dict:
        """Evaluate a candidate's answer"""
        print(f"\nEvaluating answer:")
        print(f"Question: {question[:100]}...")
        print(f"Answer: {answer[:100]}...")
        print(f"Difficulty: {difficulty}")
        
        prompt = f"""You are evaluating a technical interview answer. Be specific and analyze the actual content.

Question ({difficulty} difficulty): {question}

Candidate's Answer: {answer}

Analyze this specific answer and provide:
1. A fair score out of 10 based on completeness, accuracy, and clarity
2. Specific feedback about THIS answer (not generic)
3. What specifically was good about THIS answer
4. What specifically could be improved in THIS answer

Return ONLY valid JSON:
{{"score": <number>, "feedback": "<specific feedback>", "strengths": "<specific strengths>", "improvements": "<specific improvements>"}}"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    Config.GROQ_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": Config.GROQ_EVAL_MODEL,
                        "messages": [
                            {"role": "system", "content": "You are a technical interviewer. Analyze each answer uniquely. Return only valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800
                    }
                )
                
                if response.status_code != 200:
                    print(f"Groq Eval Error: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=response.status_code, detail=response.text)
                
                result = response.json()
                evaluation_text = result['choices'][0]['message']['content']
                
                print(f"Raw evaluation: {evaluation_text[:200]}...")
                
                # Clean up
                evaluation_text = evaluation_text.strip()
                evaluation_text = re.sub(r'^```json\s*', '', evaluation_text)
                evaluation_text = re.sub(r'^```\s*', '', evaluation_text)
                evaluation_text = re.sub(r'\s*```$', '', evaluation_text)
                evaluation_text = evaluation_text.strip()
                
                evaluation = json.loads(evaluation_text)
                
                print(f"Evaluated - Score: {evaluation.get('score')}/10")
                
                return evaluation
        
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error in evaluation: {str(e)}")
            return {
                "score": 7,
                "feedback": f"Your answer addresses the question. {answer[:50]}...",
                "strengths": "You provided a response and attempted to answer the question.",
                "improvements": "Try to provide more specific details and examples in your answers."
            }
        
        except Exception as e:
            print(f"Evaluation Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
