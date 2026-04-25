# ==============================================================================
# Landing App — Forms
# ==============================================================================
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Project, ProjectCategory


# ==============================================================================
# UNIFIED LOGIN FORM — Email/Username + Password
# ==============================================================================

class UnifiedLoginForm(forms.Form):
    """Single login form. Accepts email or username + password."""

    login_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'login-input',
            'placeholder': 'Email or Username',
            'autocomplete': 'username',
            'id': 'login-id',
        }),
        label='Email or Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'login-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
            'id': 'login-password',
        }),
        label='Password'
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        login_id = self.cleaned_data.get('login_id', '').strip()
        password = self.cleaned_data.get('password')

        if login_id and password:
            # Try username first
            self.user_cache = authenticate(
                self.request, username=login_id, password=password
            )

            # If that fails and login_id looks like an email, try email lookup
            if self.user_cache is None and '@' in login_id:
                try:
                    user_obj = User.objects.get(email__iexact=login_id)
                    self.user_cache = authenticate(
                        self.request, username=user_obj.username, password=password
                    )
                except User.DoesNotExist:
                    pass

            if self.user_cache is None:
                raise forms.ValidationError(
                    'Invalid credentials. Please check your email/username and password.',
                    code='invalid_login'
                )
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


# ==============================================================================
# LEGACY FORMS — Kept for backwards compatibility
# ==============================================================================

class AdminLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Invalid credentials.')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class MemberLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user_obj = User.objects.get(email__iexact=email)
                self.user_cache = authenticate(self.request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
            if self.user_cache is None:
                raise forms.ValidationError('Invalid credentials.')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class CECPLoginForm(AuthenticationForm):
    pass


# ==============================================================================
# PROJECT SUBMISSION FORM
# ==============================================================================

class ProjectSubmissionForm(forms.ModelForm):
    tech_stack_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., Python, OpenCV, Arduino (comma-separated)',
        }),
        help_text="Comma-separated list of technologies used"
    )

    class Meta:
        model = Project
        fields = [
            'title', 'codename', 'description', 'spec',
            'image', 'category', 'status',
            'github_url', 'demo_url', 'documentation_url',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Project Title'}),
            'codename': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Internal Codename'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Brief description...', 'rows': 3}),
            'spec': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Full technical specification...', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'github_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://github.com/...'}),
            'demo_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://demo.example.com'}),
            'documentation_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://docs.example.com'}),
        }

    def clean_tech_stack_input(self):
        raw = self.cleaned_data.get('tech_stack_input', '')
        if raw:
            return [t.strip() for t in raw.split(',') if t.strip()]
        return []

# ==============================================================================
# USER REGISTRATION FORM
# ==============================================================================

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'login-input',
        'placeholder': 'Password',
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'login-input',
        'placeholder': 'Confirm Password',
    }))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'login-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'login-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'login-input', 'placeholder': 'Email Address'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
