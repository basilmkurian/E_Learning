from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Course

class RegistrationForm(forms.ModelForm):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','username', 'password', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.create(user=user, role=self.cleaned_data['role'])
        return user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

class AssignInstructorForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    instructor = forms.ModelChoiceField(queryset=UserProfile.objects.filter(role='instructor'))