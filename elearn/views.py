from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import UserProfile, Course, Enrollment
from .forms import RegistrationForm, CourseForm, AssignInstructorForm
from django.contrib.auth import login
from django.contrib.auth.models import User

class HomeView(View):
    def get(self, request):
        return render(request, 'elearn/home.html')

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'elearn/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'elearn/register.html', {'form': form})

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        last_accessed_course_id = request.session.get('last_accessed_course')
        # If a course ID exists, get the course
        if last_accessed_course_id:
            last_accessed_course = Course.objects.get(id=last_accessed_course_id)
        else:
            last_accessed_course = None 

        if profile.role == 'student':
            enrolled_courses = Course.objects.filter(enrollment__student=profile)
            available_courses = Course.objects.exclude(enrollment__student=profile)
            return render(request, 'elearn/student_dashboard.html', {
                'enrolled_courses': enrolled_courses,
                'available_courses': available_courses,
                'last_accessed_course': last_accessed_course
            })
        
        elif profile.role == 'instructor':
            instructor_courses = Course.objects.filter(instructor=profile)
            # Check for edit action
            edit_course_id = request.GET.get('edit')
            if edit_course_id:
                course = get_object_or_404(Course, id=edit_course_id, instructor=profile)
                form = CourseForm(instance=course)
                return render(request, 'elearn/course_form.html', {'form': form, 'course': course})
            # Check for delete action
            delete_course_id = request.GET.get('delete')
            if delete_course_id:
                course = get_object_or_404(Course, id=delete_course_id, instructor=profile)
                course.delete()
                return redirect('dashboard')
            # For each course, get the list of enrolled students
            courses_with_students = []
            for course in instructor_courses:
                enrolled_students = Enrollment.objects.filter(course=course)
                students = [enrollment.student for enrollment in enrolled_students]
                courses_with_students.append({'course': course, 'students': students})
            return render(request, 'elearn/instructor_dashboard.html', {
                'courses': instructor_courses,
                'courses_with_students': courses_with_students,
            })
        
        elif profile.role == 'admin':
            users = UserProfile.objects.all()
            courses = Course.objects.all()
            user_form = RegistrationForm()
            course_form = CourseForm()
            assign_instructor_form = AssignInstructorForm()
            
            return render(request, 'elearn/admin_dashboard.html', {
                'users': users,
                'courses': courses,
                'user_form': user_form,
                'course_form': course_form,
                'assign_instructor_form': assign_instructor_form
            })
        
        else:
            return redirect('home')
        
    def post(self, request):
        profile = UserProfile.objects.get(user=request.user)
        
        if profile.role == 'admin':
            # Handle admin actions based on which form was submitted
            if 'add_user' in request.POST:
                user_form = RegistrationForm(request.POST)
                if user_form.is_valid():
                    user_form.save()
            elif 'add_course' in request.POST:
                course_form = CourseForm(request.POST)
                if course_form.is_valid():
                    course_form.save()
            elif 'assign_instructor' in request.POST:
                assign_instructor_form = AssignInstructorForm(request.POST)
                if assign_instructor_form.is_valid():
                    course = assign_instructor_form.cleaned_data['course']
                    instructor = assign_instructor_form.cleaned_data['instructor']
                    course.instructor = instructor
                    course.save()
            elif 'delete_user' in request.POST:
                user_id = request.POST.get('user_id')
                user = get_object_or_404(User, id=user_id)
                user.delete()  
            
            elif 'delete_course' in request.POST:
                course_id = request.POST.get('course_id')
                course = get_object_or_404(Course, id=course_id)
                course.delete() 
            
            elif 'unassign_instructor' in request.POST:
                course_id = request.POST.get('course_id')
                course = get_object_or_404(Course, id=course_id)
                course.instructor = None  
                course.save()
            return redirect('dashboard')

class EnrollView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        profile = UserProfile.objects.get(user=request.user)
        if profile.role == 'student':
            course = get_object_or_404(Course, id=course_id)
            created = Enrollment.objects.get_or_create(student=profile, course=course)
            if created:
                return redirect('dashboard')
            else:
                return redirect('dashboard')
        return redirect('dashboard')

class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return UserProfile.objects.get(user=self.request.user).role == 'instructor'

    def get(self, request):
        form = CourseForm()
        return render(request, 'elearn/course_form.html', {'form': form})

    def post(self, request):
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = UserProfile.objects.get(user=request.user)
            course.save()
            return redirect('dashboard')
        return render(request, 'elearn/course_form.html', {'form': form})

class CourseDetailView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        request.session['last_accessed_course'] = course.id
        return render(request, 'elearn/course_detail.html', {'course': course})