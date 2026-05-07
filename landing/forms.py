# ==============================================================================
# Landing App — Forms
# ==============================================================================
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Project, ProjectCategory, ClubApplication


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

    # Dynamic team members (handled via JS, sent as JSON list of dicts)
    team_members_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'team_member_emails_json'}),
        help_text="JSON array of team member objects [{'name': '', 'email': ''}]"
    )

    # Dynamic achievements (handled via JS, sent as JSON)
    achievements_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'achievements_json'}),
        help_text="JSON array of achievement objects"
    )

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'spec',
            'image', 'category', 'status', 'year',
            'github_url', 'demo_url', 'documentation_file', 'video_url',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Project Title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Brief description...', 'rows': 3}),
            'spec': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Full technical specification...', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'year': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '2026', 'min': '2020', 'max': '2035'}),
            'github_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://github.com/your-username/your-repo'}),
            'demo_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://drive.google.com/...'}),
            'video_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://youtube.com/watch?v=...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make GitHub URL required
        self.fields['github_url'].required = True
        self.fields['github_url'].help_text = 'Only GitHub links are accepted (mandatory)'
        # Make documentation file required
        self.fields['documentation_file'].required = True
        self.fields['documentation_file'].help_text = 'Upload your documentation/paper/PPT file (mandatory)'
        self.fields['documentation_file'].widget = forms.FileInput(attrs={
            'class': 'w-full text-sm text-slate-400 file:mr-4 file:py-2.5 file:px-5 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-slate-800 file:text-white hover:file:bg-slate-700 file:transition-colors file:cursor-pointer border border-slate-800 rounded-xl p-1.5 bg-slate-900/50',
            'accept': '.pdf,.doc,.docx,.ppt,.pptx',
            'id': 'id_documentation_file',
        })
        # Keep video_url optional
        self.fields['video_url'].required = False
        # Keep demo_url optional
        self.fields['demo_url'].required = False
        self.fields['demo_url'].help_text = 'Only Google Drive links are accepted'

    def clean_github_url(self):
        """Validate that the repository URL is a GitHub link."""
        url = self.cleaned_data.get('github_url', '').strip()
        if not url:
            raise forms.ValidationError('GitHub repository link is required.')
        if not (url.startswith('https://github.com/') or url.startswith('http://github.com/') or url.startswith('https://www.github.com/') or url.startswith('http://www.github.com/')):
            raise forms.ValidationError('Only GitHub links are allowed (must start with https://github.com/).')
        return url

    def clean_demo_url(self):
        """Validate that the live demo URL is a Google Drive link (if provided)."""
        url = self.cleaned_data.get('demo_url', '').strip()
        if not url:
            return url  # optional field
        if not (url.startswith('https://drive.google.com/') or url.startswith('http://drive.google.com/')):
            raise forms.ValidationError('Only Google Drive links are allowed for Live Demo (must start with https://drive.google.com/).')
        return url

    def clean_documentation_file(self):
        """Validate the uploaded documentation file."""
        f = self.cleaned_data.get('documentation_file')
        if not f:
            raise forms.ValidationError('Documentation/Paper/PPT file is required.')
        # Validate file extension
        allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
        import os
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in allowed_extensions:
            raise forms.ValidationError(f'Invalid file type ({ext}). Allowed: PDF, DOC, DOCX, PPT, PPTX.')
        # Limit file size to 25MB
        if f.size > 25 * 1024 * 1024:
            raise forms.ValidationError('File size must be under 25MB.')
        return f

    def clean_tech_stack_input(self):
        raw = self.cleaned_data.get('tech_stack_input', '')
        if raw:
            return [t.strip() for t in raw.split(',') if t.strip()]
        return []

    def clean_team_members_json(self):
        import json
        raw = self.cleaned_data.get('team_members_json', '')
        if not raw:
            return []
        try:
            members = json.loads(raw)
            if not isinstance(members, list):
                return []
            cleaned = []
            for mem in members:
                if isinstance(mem, dict):
                    email = str(mem.get('email', '')).strip().lower()
                    name = str(mem.get('name', '')).strip()
                    if email and '@' in email:
                        cleaned.append({'name': name, 'email': email})
            return cleaned
        except (json.JSONDecodeError, TypeError):
            return []

    def clean_achievements_json(self):
        import json
        raw = self.cleaned_data.get('achievements_json', '')
        if not raw:
            return []
        try:
            achievements = json.loads(raw)
            if not isinstance(achievements, list):
                return []
            cleaned = []
            for ach in achievements:
                if isinstance(ach, dict) and ach.get('title') and ach.get('date'):
                    cleaned.append({
                        'title': str(ach['title'])[:300],
                        'achievement_type': str(ach.get('achievement_type', 'competition'))[:20],
                        'event_name': str(ach.get('event_name', ''))[:200],
                        'position': str(ach.get('position', ''))[:100],
                        'description': str(ach.get('description', ''))[:500],
                        'date': str(ach['date']),
                        'certificate_url': str(ach.get('certificate_url', ''))[:200],
                    })
            return cleaned
        except (json.JSONDecodeError, TypeError):
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


# ==============================================================================
# CLUB APPLICATION FORM — "Join the Club"
# ==============================================================================

class ClubApplicationForm(forms.ModelForm):
    """
    Application form for prospective CECP members.
    Enforces @ritroorkee.com email on both frontend (pattern attr) and backend.
    """

    class Meta:
        model = ClubApplication
        fields = [
            'full_name', 'profile_photo', 'resume', 'email', 'personal_email', 'whatsapp_number', 'roll_number',
            'branch', 'current_year', 'domain_of_interest',
            'skill_level', 'motivation', 'quote',
            'github_url', 'linkedin_url',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'apply-input', 'placeholder': 'Your full name',
                'id': 'id_full_name',
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'apply-input file-input', 
                'id': 'id_profile_photo',
                'accept': 'image/*'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'apply-input file-input', 
                'id': 'id_resume',
                'accept': '.pdf,.doc,.docx'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'apply-input', 'placeholder': 'yourname@ritroorkee.com',
                'pattern': '.+@ritroorkee\\.com',
                'title': 'Please use your official @ritroorkee.com email',
                'id': 'id_email',
            }),
            'personal_email': forms.EmailInput(attrs={
                'class': 'apply-input', 'placeholder': 'yourname@gmail.com',
                'title': 'This email will be used for your Google Login',
                'id': 'id_personal_email',
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'apply-input', 'placeholder': '+91 XXXXX XXXXX',
                'id': 'id_whatsapp',
            }),
            'roll_number': forms.TextInput(attrs={
                'class': 'apply-input', 'placeholder': 'e.g., 22ECE001',
                'id': 'id_roll',
            }),
            'branch': forms.Select(attrs={
                'class': 'apply-input', 'id': 'id_branch',
            }),
            'current_year': forms.Select(attrs={
                'class': 'apply-input', 'id': 'id_year',
            }),
            'domain_of_interest': forms.Select(attrs={
                'class': 'apply-input', 'id': 'id_domain',
            }),
            'skill_level': forms.RadioSelect(attrs={
                'id': 'id_skill_level',
            }),
            'motivation': forms.Textarea(attrs={
                'class': 'apply-input', 'rows': 4,
                'placeholder': 'Tell us what excites you about CECP and what you hope to learn or contribute...',
                'id': 'id_motivation',
            }),
            'quote': forms.TextInput(attrs={
                'class': 'apply-input', 'placeholder': 'Your personal quote or signature phrase (Optional)',
                'id': 'id_quote',
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'apply-input', 'placeholder': 'https://github.com/yourusername',
                'id': 'id_github',
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'apply-input', 'placeholder': 'https://linkedin.com/in/yourprofile',
                'id': 'id_linkedin',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the empty "---------" choice for the RadioSelect widget
        self.fields['skill_level'].choices = self.Meta.model.SKILL_CHOICES

    def clean_email(self):
        """Backend enforcement: only @ritroorkee.com emails allowed."""
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email.endswith('@ritroorkee.com'):
            raise forms.ValidationError(
                "Only @ritroorkee.com email addresses are accepted. "
                "Please use your official college email."
            )
        # Check for duplicate applications
        qs = ClubApplication.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "An application with this email already exists."
            )
        return email

class ClubApplicationReviewForm(forms.ModelForm):
    """
    Form for moderators to review, assign roles/categories, and approve/reject applications.
    """
    class Meta:
        model = ClubApplication
        fields = [
            'status', 'assigned_category', 'assigned_role',
            'rejection_reason', 'send_notification_email'
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full rounded-md bg-slate-900/50 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500'
            }),
            'assigned_category': forms.Select(attrs={
                'class': 'w-full rounded-md bg-slate-900/50 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500'
            }),
            'assigned_role': forms.TextInput(attrs={
                'class': 'w-full rounded-md bg-slate-900/50 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': 'e.g., UI/UX Lead, Web Master'
            }),
            'rejection_reason': forms.Textarea(attrs={
                'class': 'w-full rounded-md bg-slate-900/50 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'rows': 3,
                'placeholder': 'If rejected, please provide a reason...'
            }),
            'send_notification_email': forms.CheckboxInput(attrs={
                'class': 'rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-cyan-500 w-5 h-5'
            }),
        }

# ==============================================================================
# USER PROFILE FORM
# ==============================================================================
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'course', 'branch', 'graduation_year',
            'college_roll_number', 'date_of_birth', 'gender',
            'hometown', 'mobile_number', 'github_profile', 'linkedin_profile',
            'quote'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-slate-300 border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500'
            }),
            'course': forms.Select(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'id': 'id_course'
            }),
            'branch': forms.Select(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'id': 'id_branch'
            }),
            'graduation_year': forms.TextInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': 'e.g., 2025-2029'
            }),
            'college_roll_number': forms.TextInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': 'e.g., 22ECE001'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500'
            }),
            'hometown': forms.TextInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': 'e.g., Patna, Bihar'
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': '+91 XXXXXXXXXX'
            }),
            'github_profile': forms.URLInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': 'https://github.com/yourusername'
            }),
            'linkedin_profile': forms.URLInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'quote': forms.TextInput(attrs={
                'class': 'w-full rounded-md bg-slate-900 p-3 text-white border border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                'placeholder': 'e.g., Build things that matter.',
                'maxlength': '100',
            }),
        }

