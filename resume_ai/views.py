from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .utils import extract_pdf_text
from .services import analyze_resume


@login_required
def upload_resume(request):

    if request.method == "POST":

        resume = request.FILES.get("resume")

        if not resume:
            return redirect("user_dashboard")

        # User profile
        profile = request.user.userprofile

        # PDF text
        raw_text = extract_pdf_text(resume)

        # AI analysis
        data = analyze_resume(raw_text)

        # Basic info
        profile.phone = data.get("phone", "")
        profile.location = data.get("location", "")

        # ---------------- SKILLS ----------------

        skills = data.get("skills", [])

        # Agar AI string bheje
        if isinstance(skills, str):
            skills = skills.split(",")

        # Clean skills
        clean_skills = []

        for skill in skills:

            skill = str(skill).strip()

            if skill and skill not in clean_skills:
                clean_skills.append(skill)

        profile.skills = ", ".join(clean_skills)

        # ---------------- PROJECTS ----------------

        projects = data.get("projects", [])

        if isinstance(projects, list):
            profile.projects = ", ".join(
                [str(p) for p in projects]
            )
        else:
            profile.projects = str(projects)

        # ---------------- EDUCATION ----------------

        education = data.get("education", [])

        if isinstance(education, list):
            profile.education = ", ".join(
                [str(e) for e in education]
            )
        else:
            profile.education = str(education)

        # ---------------- EXPERIENCE ----------------

        experience = data.get("experience", [])

        if isinstance(experience, list):
            profile.experience = ", ".join(
                [str(e) for e in experience]
            )
        else:
            profile.experience = str(experience)

        # ATS Score
        ats_score = data.get("ats_score")
        if not ats_score:
            ats_score = 0

        profile.ats_score = int(ats_score)

        # Resume save
        profile.resume = resume

        # Profile completed
        profile.profile_completed = True

        # Save profile
        profile.save()

    return redirect("user_dashboard")