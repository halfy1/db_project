from django import forms
from .models import Project, Employee, Feature, Bug

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'date_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'date_employment': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_dismissal': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = '__all__'
        widgets = {
            'date_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = '__all__'
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reported_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fixed_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }