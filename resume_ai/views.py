from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from job.models import UserProfile
from .utils import extract_pdf_text
from .services import analyze_resume


@login_required
def upload_resume(request):

    if request.method == "POST":

        resume = request.FILES.get("resume")

        if not resume:
            return redirect("home")

        raw_text = extract_pdf_text(resume)

        data = analyze_resume(raw_text)

        profile = request.user.userprofile

        profile.phone = data.get("phone", "")
        profile.location = data.get("location", "")
        profile.skills = ", ".join([str(x) for x in data.get("skills", [])])

        profile.projects = ", ".join(
            [
                x.get("name", str(x)) if isinstance(x, dict) else str(x)
                for x in data.get("projects", [])
            ]
        )

        profile.education = ", ".join([str(x) for x in data.get("education", [])])

        profile.experience = ", ".join([str(x) for x in data.get("experience", [])])
        profile.ats_score = data.get("ats_score", 0)
        profile.resume = resume
        profile.profile_completed = True

        profile.save()

    return redirect("user_dashboard")
