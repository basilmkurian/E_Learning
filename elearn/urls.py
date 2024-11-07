from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='elearn/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('enroll/<int:course_id>/', views.EnrollView.as_view(), name='enroll'),
    path('course/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('course/<int:course_id>/', views.CourseDetailView.as_view(), name='course_detail'),
]
