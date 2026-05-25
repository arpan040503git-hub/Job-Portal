import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_resume(text):

    prompt = f"""
You are an expert resume parser.

Extract information from this resume.

IMPORTANT RULES:
- Extract ALL technical skills
- Include programming languages
- Include frameworks
- Include tools
- Include databases
- Include projects
- Include education
- Include work experience
- Return ONLY valid JSON
- skills MUST be a JSON array

Return format:
{{
    "phone": "",
    "location": "",
    "skills": [],
    "projects": [],
    "education": [],
    "experience": [],
    "ats_score": 0
}}

RESUME TEXT:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content
        return json.loads(result)

    except Exception as e:
        print("Resume Analysis Error:", e)

        return {
            "phone": "",
            "location": "",
            "skills": [],
            "projects": [],
            "education": [],
            "experience": [],
            "ats_score": 0
        }


def analyze_job_match(resume_text, job):

    prompt = f"""
Compare the resume with the job and return ONLY valid JSON.

Return format:
{{
    "ats_score": 0,
    "matched_skills": [],
    "missing_skills": [],
    "suggestions": []
}}

JOB TITLE:
{job.title}

JOB DESCRIPTION:
{job.description}

RESPONSIBILITIES:
{job.responsibilities}

REQUIRED SKILLS:
{job.skills}

RESUME:
{resume_text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content
        return json.loads(result)

    except Exception as e:
        print("Job Match Error:", e)

        return {
            "ats_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": []
        }