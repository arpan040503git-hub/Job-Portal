from django.shortcuts import render, get_object_or_404, redirect
from .models import Job, Profile, UserProfile, ClientProfile,Application
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from resume_ai.services import analyze_job_match
from resume_ai.utils import extract_pdf_text
from django.contrib import admin



# REGISTER
def register(request):
    error = ''

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        profile_pic = request.FILES.get('profile_pic')

        if User.objects.filter(username=username).exists():
            error = "User Already Exists"

        elif password != confirm_password:
            error = "Passwords do not match"

        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            Profile.objects.create(
                user=user,
                role=role,
                profile_pic=profile_pic
            )

            if role == "user":
                UserProfile.objects.create(
                    user=user
                )

            else:
                ClientProfile.objects.create(
                    user=user
                )

            return redirect("login")

    return render(
        request,
        'job/register.html',
        {
            'error': error
        }
    )

# LOGIN
def user_login(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("/admin")

            if user.profile.role == "client":
                return redirect("client_dashboard")

            return redirect("home")

        else:
            error = "Invalid Username or Password"

    return render(request, "job/login.html", {"error": error})


# LOGOUT
def user_logout(request):
    logout(request)
    return redirect("home")


# CLIENT DASHBOARD
@login_required
def client_dashboard(request):

    if request.user.profile.role != "client":
        return redirect("home")

    edit_job_obj = None

    edit_id = request.GET.get("edit")

    if edit_id:
        edit_job_obj = get_object_or_404(
            Job,
            id=edit_id,
            posted_by=request.user
        )

    if request.method == "POST":

        job_id = request.POST.get("job_id")

        # UPDATE EXISTING JOB
        if job_id:

            job = get_object_or_404(
                Job,
                id=job_id,
                posted_by=request.user
            )

            job.title = request.POST.get("title")
            job.company = request.POST.get("company")
            job.location = request.POST.get("location")
            job.job_type = request.POST.get("job_type")
            job.salary = request.POST.get("salary")
            job.description = request.POST.get("description")
            job.responsibilities = request.POST.get("responsibilities")
            job.skills = request.POST.get("skills")

            job.save()

        # CREATE NEW JOB
        else:

            Job.objects.create(
                posted_by=request.user,
                title=request.POST.get("title"),
                company=request.POST.get("company"),
                location=request.POST.get("location"),
                job_type=request.POST.get("job_type"),
                salary=request.POST.get("salary"),
                description=request.POST.get("description"),
                responsibilities=request.POST.get("responsibilities"),
                skills=request.POST.get("skills"),
            )

        return redirect("client_dashboard")

    jobs = Job.objects.filter(
    posted_by=request.user
    ).order_by("-created_at")

    total_posts = jobs.count()

    total_applicants = Application.objects.filter(
        job__posted_by=request.user
    ).count()
    applications = Application.objects.filter(
        job__posted_by=request.user
    ).select_related("user", "job").order_by("-applied_at")

    return render(
        request,
        "job/client_dashboard.html",
        {
            "jobs": jobs,
            "edit_job": edit_job_obj,
            "total_posts": total_posts,
            "total_applicants": total_applicants,
            "applications": applications,
        }
    )


# DELETE JOB
@login_required
def delete_job(request, id):

    if request.user.profile.role != "client":
        return redirect("home")

    job = get_object_or_404(
        Job,
        id=id,
        posted_by=request.user
    )

    if request.method == "POST":
        job.delete()

    return redirect("client_dashboard")

# USER DASHBOARD
@login_required
def user_dashboard(request):

    if request.user.profile.role != "user":
        return redirect("home")

    profile = request.user.userprofile

    applications = Application.objects.filter(
        user=request.user
    ).order_by('-applied_at')

    matched_jobs = Job.objects.none()
    skills_list = []

    if profile.skills:

        skills_list = [
            skill.strip()
            for skill in profile.skills.split(",")
            if skill.strip()
        ]

        print("PROFILE SKILLS:", profile.skills)
        print("SKILLS LIST:", skills_list)

        if skills_list:
            query = Q()

            for skill in skills_list:
                query |= Q(skills__icontains=skill)

            matched_jobs = Job.objects.filter(query).distinct()[:5]

    context = {
        "profile": profile,
        "matched_jobs": matched_jobs,
        "skills_list": skills_list,
        "applications": applications,
        "applied_count": applications.count(),
    }

    return render(
        request,
        'job/user_dashboard.html',
        context
    )
#_____________________APPLICATION________________________________

@login_required
def apply_job(request, job_id):

    if request.user.profile.role != "user":
        return redirect("home")

    job = get_object_or_404(
        Job,
        id=job_id
    )

    already_applied = Application.objects.filter(
        user=request.user,
        job=job
    ).exists()

    if not already_applied:
        Application.objects.create(
            user=request.user,
            job=job,
            company_name=job.company
        )

    return redirect(f"/?job_id={job.id}")

# FILTER JOBS
def get_filtered_jobs(request):
    jobs = Job.objects.all().order_by("-created_at")

    search = request.GET.get("search")
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company__icontains=search)
            | Q(skills__icontains=search)
            | Q(location__icontains=search)
        )

    title = request.GET.get("title")
    if title:
        jobs = jobs.filter(title=title)

    location = request.GET.get("location")
    if location:
        jobs = jobs.filter(location=location)

    job_type = request.GET.get("job_type")
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    return jobs


# SELECT JOB
def get_selected_job(request, jobs):
    job_id = request.GET.get("job_id")

    if job_id:
        return get_object_or_404(Job, id=job_id)

    return jobs.first()

# HOME
def home(request):

    titles = Job.objects.values_list("title", flat=True).distinct()
    types = Job.objects.exclude(job_type="").values_list("job_type", flat=True).distinct()
    locations = Job.objects.exclude(location="").values_list("location", flat=True).distinct()

    jobs = get_filtered_jobs(request)
    ats_data = None

    # SAFE PROFILE ACCESS
    profile = getattr(request.user, "profile", None)

    # Resume skills ke hisaab se matched jobs upar lao
    if request.user.is_authenticated and profile and profile.role == "user":
        user_profile = getattr(request.user, "userprofile", None)

        if user_profile and user_profile.skills:
            skills_list = [
                skill.strip()
                for skill in user_profile.skills.split(",")
                if skill.strip()
            ]

            if skills_list:
                query = Q()

                for skill in skills_list:
                    query |= Q(skills__icontains=skill)

                matched_jobs = jobs.filter(query).distinct()
                other_jobs = jobs.exclude(
                    id__in=matched_jobs.values_list("id", flat=True)
                )

                jobs = list(matched_jobs) + list(other_jobs)

    # selected job after sorting
    selected_job = jobs[0] if jobs else None

    job_id = request.GET.get("job_id")
    if job_id:
        selected_job = get_object_or_404(Job, id=job_id)

    # ATS score
    if request.user.is_authenticated and profile and profile.role == "user":
        user_profile = getattr(request.user, "userprofile", None)

        if user_profile and user_profile.resume and selected_job:
            import os

            if os.path.exists(user_profile.resume.path):
                resume_text = extract_pdf_text(user_profile.resume)
                ats_data = analyze_job_match(resume_text, selected_job)

    job_skills = []
    job_responsibilities = []

    if selected_job:
        if selected_job.skills:
            job_skills = [s.strip() for s in selected_job.skills.split(",")]

        if selected_job.responsibilities:
            job_responsibilities = selected_job.responsibilities.splitlines()

    return render(
        request,
        'job/index.html',
        {
            "jobs": jobs,
            "s_job": selected_job,
            "titles": titles,
            "locations": locations,
            "types": types,
            "job_skills": job_skills,
            "job_responsibilities": job_responsibilities,
            "show_resume_popup": (
                request.user.is_authenticated
                and profile
                and profile.role == "user"
                and hasattr(request.user, "userprofile")
                and not request.user.userprofile.profile_completed
            ),
            "ats_data": ats_data,
        }
    )    