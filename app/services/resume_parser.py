"""Resume parsing service"""
import re
from fastapi import HTTPException
import PyPDF2
from docx import Document

class ResumeParser:
    """Service for parsing resumes and extracting information"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> dict:
        """Parse PDF resume"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            return ResumeParser.extract_info(text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def parse_docx(file_path: str) -> dict:
        """Parse DOCX resume"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            return ResumeParser.extract_info(text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path: str) -> dict:
        """Parse TXT resume"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            return ResumeParser.extract_info(text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing TXT: {str(e)}")
    
    @staticmethod
    def extract_info(text: str) -> dict:
        """Extract information from resume text"""
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Extract skills
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'nodejs',
            'django', 'flask', 'fastapi', 'sql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'git', 'github',
            'machine learning', 'ml', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
            'data science', 'html', 'css', 'typescript', 'c++', 'c#', 'go', 'golang', 'rust',
            'ruby', 'php', 'swift', 'kotlin', 'express', 'restful', 'graphql', 'api',
            'microservices', 'agile', 'scrum', 'ci/cd', 'jenkins', 'linux', 'bash', 'powershell',
            'pandas', 'numpy', 'matplotlib', 'spring', 'hibernate', '.net', 'asp.net',
            'elasticsearch', 'kafka', 'rabbitmq', 'terraform', 'ansible', 'chef', 'puppet'
        ]
        
        skills_found = []
        for skill in common_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                skills_found.append(skill.title())
        
        skills_found = list(dict.fromkeys(skills_found))[:15]
        
        # Extract certifications
        certifications = []
        cert_patterns = [
            r'.*(?:aws|amazon|microsoft|azure|google|oracle|cisco|comptia|red hat|ibm|salesforce).*certified.*',
            r'.*certification.*(?:aws|azure|google|oracle|cisco|python|java|pmp|scrum).*',
            r'.*(?:certified|certification).*'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and len(line_stripped) > 10:
                for pattern in cert_patterns:
                    if re.search(pattern, line.lower()):
                        if not any(exclude in line.lower() for exclude in ['experience', 'education', 'skills', 'summary', 'projects', 'objective']):
                            certifications.append(line_stripped)
                            break
        
        certifications = list(dict.fromkeys(certifications))[:5]
        
        # Extract hobbies
        hobbies = []
        capture = False
        section_end_keywords = ['experience', 'education', 'skills', 'projects', 'certifications', 'languages', 'volunteer']
        
        for line in lines:
            line_stripped = line.strip()
            
            if re.search(r'^(hobbies|interests|activities|personal interests)', line.lower()):
                capture = True
                continue
            
            if capture and any(re.search(r'^' + keyword, line.lower()) for keyword in section_end_keywords):
                break
            
            if capture and line_stripped:
                if len(line_stripped) < 100 and ':' not in line_stripped[:15]:
                    cleaned = re.sub(r'^[-•*]\s*', '', line_stripped)
                    if cleaned:
                        hobbies.append(cleaned)
        
        hobbies = hobbies[:5]
        
        # Extract experience
        experience = "Not specified"
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                years = match.group(1)
                experience = f"{years}+ years"
                break
        
        print(f"Extracted - Skills: {len(skills_found)}, Certs: {len(certifications)}, Hobbies: {len(hobbies)}")
        
        return {
            "skills": skills_found if skills_found else ["Python", "JavaScript", "Web Development"],
            "certifications": certifications,
            "hobbies": hobbies,
            "experience": experience
        }
