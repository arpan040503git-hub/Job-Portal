from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .utils import extract_pdf_text
from .services import analyze_resume
import re


@login_required
def upload_resume(request):

    if request.method == "POST":

        resume = request.FILES.get("resume")

        if not resume:
            return redirect("user_dashboard")

        profile = request.user.userprofile

        raw_text = extract_pdf_text(resume)
        data = analyze_resume(raw_text)

        profile.phone = data.get("phone", "")
        profile.location = data.get("location", "")

        # SKILLS
        skills = data.get("skills", [])

        if not skills:
            common_skills = [
                "Python", "Django", "HTML", "CSS", "JavaScript",
                "React.js", "Node.js", "Express.js", "MongoDB",
                "MySQL", "SQLite", "Git", "GitHub", "PHP", "C++"
            ]

            found_skills = []

            for skill in common_skills:
                if skill.lower() in raw_text.lower():
                    found_skills.append(skill)

            skills = found_skills

        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]

        profile.skills = ", ".join([str(x) for x in skills])

        # PROJECTS
        projects = data.get("projects", [])

        if isinstance(projects, list):
            clean_projects = []

            for item in projects:
                if isinstance(item, dict):
                    clean_projects.append(
                        item.get("name", str(item))
                    )
                else:
                    clean_projects.append(str(item))

            profile.projects = ", ".join(clean_projects)

        else:
            profile.projects = str(projects)

        # EDUCATION
        education = data.get("education", [])

        if isinstance(education, list):
            clean_education = []

            for item in education:
                if isinstance(item, dict):
                    clean_education.append(
                        item.get("degree", str(item))
                    )
                else:
                    clean_education.append(str(item))

            profile.education = ", ".join(clean_education)

        else:
            profile.education = str(education)

        # EXPERIENCE
        experience = data.get("experience", [])

        if isinstance(experience, list):
            clean_experience = []

            for item in experience:
                if isinstance(item, dict):
                    clean_experience.append(
                        item.get("title", str(item))
                    )
                else:
                    clean_experience.append(str(item))

            profile.experience = ", ".join(clean_experience)

        else:
            profile.experience = str(experience)

        # PHONE FALLBACK
        if not profile.phone:
            phone_match = re.search(r'\b\d{10}\b', raw_text)
            if phone_match:
                profile.phone = phone_match.group()

        # LOCATION FALLBACK
        if not profile.location:
            if "Lucknow" in raw_text:
                profile.location = "Lucknow"

        profile.ats_score = int(data.get("ats_score") or 75)
        profile.resume = resume
        profile.profile_completed = True
        profile.save()

    return redirect("user_dashboard")