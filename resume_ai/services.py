import json
from groq import Groq
from django.conf import settings


client = Groq( 
    api_key=settings.GROQ_API_KEY
)


def analyze_resume(text):

    prompt = f"""
    Analyze this resume.

    Return ONLY valid JSON.

    {{
        "phone": "",
        "location": "",
        "skills": [],
        "projects": [],
        "education": [],
        "experience": [],
        "ats_score": 0
    }}

    Resume:
    {text}
    """

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