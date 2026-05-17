from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = (
        ("client", "Client"),
        ("user", "User"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    profile_pic = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.user.username


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=20, blank=True)

    location = models.CharField(max_length=200, blank=True)

    skills = models.TextField(blank=True)

    projects = models.TextField(blank=True)

    education = models.TextField(blank=True)

    experience = models.TextField(blank=True)

    ats_score = models.IntegerField(default=0)

    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class ClientProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=200, blank=True)

    company_email = models.EmailField(blank=True)

    company_location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.company_name


class Job(models.Model):

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=200)

    company = models.CharField(max_length=200)

    location = models.CharField(max_length=200)

    job_type = models.CharField(max_length=50)

    salary = models.IntegerField()

    description = models.TextField()

    responsibilities = models.TextField(blank=True)

    skills = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Application(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Interview', 'Interview'),
        ('Rejected', 'Rejected'),
        ('Selected', 'Selected'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    company_name = models.CharField(
        max_length=200
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"