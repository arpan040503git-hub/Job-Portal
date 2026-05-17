from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("client-dashboard/", views.client_dashboard, name="client_dashboard"),
    path("user-dashboard/", views.user_dashboard, name="user_dashboard"),
    path("edit-job/<int:id>/", views.edit_job, name="edit_job"),
    path("delete-job/<int:id>/", views.delete_job, name="delete_job"),
    path("apply-job/<int:job_id>/", views.apply_job, name="apply_job"),
]
