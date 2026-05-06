# ==============================================================================
# Landing App — Data Models
# ==============================================================================
# Professional-grade models for the CECP club website.
# Implements: Role-based ClubMember system, Project approval workflow,
# Category taxonomy, and in-app Notifications.
# ==============================================================================
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from cloudinary_storage.storage import RawMediaCloudinaryStorage


# ==============================================================================
# GLOBAL CHOICES — Single source of truth for member hierarchy
# ==============================================================================

CATEGORY_CHOICES = [
    ('advisor', 'Faculty Advisor'),
    ('head', 'Club Head'),
    ('core', 'Core Team'),
    ('member', 'Club Member'),
]


# ==============================================================================
# CLUB MEMBER — Role-based access control + Team page source of truth
# ==============================================================================

class ClubMember(models.Model):
    """
    Links a Django User to a CECP club role.
    Role hierarchy: HOD > Faculty > Club Head > Member
    This is also the SINGLE SOURCE OF TRUTH for the public Team page.
    """
    ROLE_CHOICES = [
        ('hod', 'HOD / Faculty Coordinator'),
        ('faculty', 'Faculty Coordinator'),
        ('club_head', 'Club Head'),
        ('member', 'Club Member'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='club_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    # --- Team Page Fields ---
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='member',
        help_text="Category on the public Team page (advisor / head / core / member)"
    )
    display_role = models.CharField(
        max_length=100, blank=True,
        help_text="Specific title shown on Team page (e.g., 'Web Master', 'Hardware Lead')"
    )

    member_id = models.CharField(
        max_length=20, unique=True, blank=True,
        help_text="Unique member ID (e.g., CECP-2025-001)"
    )
    display_name = models.CharField(max_length=200, blank=True, help_text="Specific title/name shown on Team page")
    profile_image = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, help_text="Short bio or specialization")
    quote = models.CharField(max_length=255, blank=True, help_text="A personal quote or signature phrase.")
    phone = models.CharField(max_length=15, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # --- Profile Detail Fields ---
    core_technologies = models.CharField(max_length=255, blank=True, help_text="Comma-separated skills (e.g., Python, React, IoT)")
    area_of_interest = models.CharField(max_length=255, blank=True, help_text="e.g., Embedded Systems, AI, Web Dev")
    experience = models.TextField(blank=True, help_text="Internships, past roles, or major accomplishments")
    
    joined_at = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.get_category_display()}"

    @property
    def is_club_head(self):
        return self.role == 'club_head'

    @property
    def is_faculty(self):
        return self.role in ('hod', 'faculty')

    @property
    def can_approve_projects(self):
        """Club Head and HOD can approve projects."""
        return self.role in ('club_head', 'hod')

    @property
    def get_display_name(self):
        return self.display_name or self.user.get_full_name() or self.user.username

    @property
    def team_role_label(self):
        """Returns display_role if set, otherwise falls back to category display."""
        return self.display_role or self.get_category_display()


# ==============================================================================
# PROJECT CATEGORY — Dynamic taxonomy
# ==============================================================================

class ProjectCategory(models.Model):
    """
    Dynamic project categories (IoT, Robotics, AI/ML, Audio, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    color = models.CharField(
        max_length=7, default='#06b6d4',
        help_text="Hex color for the category badge (e.g., #06b6d4)"
    )
    icon_class = models.CharField(max_length=50, blank=True, help_text="Optional icon identifier")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Project Categories'

    def __str__(self):
        return self.name


# ==============================================================================
# PROJECT — Full project with approval workflow
# ==============================================================================

class Project(models.Model):
    is_approved = models.BooleanField(default=False)
    """
    Represents a club project with full approval workflow.
    Members submit → Club Head approves → appears on live site.
    """
    STATUS_CHOICES = [
        ('active', 'Active / Ongoing'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    APPROVAL_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Pro', 'Pro'),
    ]

    # --- Core Fields ---
    title = models.CharField(max_length=200, help_text="Project title")
    codename = models.CharField(max_length=100, blank=True, help_text="Internal codename")
    description = models.TextField(help_text="Brief project description (shown on card)")
    spec = models.TextField(blank=True, help_text="Full technical specification (for AI categorization)")

    # --- Media ---
    image = models.ImageField(upload_to='projects/', blank=True, null=True, help_text="Project thumbnail")

    # --- Classification ---
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='projects'
    )
    tech_stack = models.JSONField(default=list, blank=True, help_text="Technologies used (JSON array)")
    level = models.CharField(
        max_length=50, choices=LEVEL_CHOICES, blank=True,
        help_text="Auto-assigned by AI based on spec"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # --- Approval Workflow ---
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_CHOICES, default='pending',
        help_text="Approval status in the review pipeline"
    )
    submitted_by = models.ForeignKey(
        ClubMember, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='submitted_projects',
        help_text="Member who submitted this project"
    )
    approved_by = models.ForeignKey(
        ClubMember, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_projects',
        help_text="Club Head / HOD who approved this project"
    )
    rejection_reason = models.TextField(blank=True, help_text="Reason if project was rejected")

    # --- Team ---
    project_lead = models.ForeignKey(
        ClubMember, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='led_projects',
        help_text="The primary lead of this project"
    )
    team_members = models.ManyToManyField(
        ClubMember, blank=True, related_name='projects',
        help_text="Members who worked on this project"
    )
    external_team_members = models.JSONField(
        default=list, blank=True,
        help_text="List of dicts [{'name': '...', 'email': '...'}] for unregistered teammates"
    )

    # --- External Links ---
    github_url = models.URLField(blank=True, help_text="GitHub repository URL")
    demo_url = models.URLField(blank=True, help_text="Live demo or video URL")
    documentation_url = models.URLField(blank=True, help_text="Documentation or report URL")
    video_url = models.URLField(blank=True, help_text="YouTube or demo video URL")

    # --- Ordering & Display ---
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Feature on the landing page")
    year = models.PositiveIntegerField(default=2026, help_text="Project year")

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_approval_status_display()})"

    @property
    def is_live(self):
        """Project is visible on the public site only if approved."""
        return self.approval_status == 'approved'


# ==============================================================================
# PROJECT ACHIEVEMENT — Competition wins, milestones, awards
# ==============================================================================

class ProjectAchievement(models.Model):
    """
    Tracks achievements / milestones / competition results for a project.
    E.g., "Top 10 Finalist — OpenAI Hackathon National Finals 2026"
    """
    ACHIEVEMENT_TYPE_CHOICES = [
        ('competition', 'Competition / Hackathon'),
        ('award', 'Award / Recognition'),
        ('publication', 'Publication / Paper'),
        ('milestone', 'Project Milestone'),
        ('deployment', 'Deployment / Launch'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='achievements',
        help_text="The project this achievement belongs to"
    )
    title = models.CharField(
        max_length=300,
        help_text="e.g., Top 10 Finalist — OpenAI Hackathon National Finals"
    )
    achievement_type = models.CharField(
        max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES, default='competition'
    )
    description = models.TextField(
        blank=True,
        help_text="Details about the achievement"
    )
    event_name = models.CharField(
        max_length=200, blank=True,
        help_text="e.g., Technomax 2025, OpenAI Hackathon 2026"
    )
    position = models.CharField(
        max_length=100, blank=True,
        help_text="e.g., 1st Place, Top 10 Finalist, Runner Up"
    )
    date = models.DateField(
        help_text="Date of the achievement"
    )
    certificate_url = models.URLField(
        blank=True,
        help_text="Link to certificate or proof"
    )
    certificate_file = models.FileField(
        upload_to='achievements/certificates/',
        blank=True, null=True,
        help_text="Upload certificate file (PDF/Image)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Project Achievement'
        verbose_name_plural = 'Project Achievements'

    def __str__(self):
        return f"{self.title} — {self.project.title} ({self.date})"


# ==============================================================================
# NOTIFICATION — In-app notification system
# ==============================================================================

class Notification(models.Model):
    """
    Simple in-app notification for the approval workflow.
    """
    TYPE_CHOICES = [
        ('submission', 'New Project Submission'),
        ('approved', 'Project Approved'),
        ('rejected', 'Project Rejected'),
        ('info', 'General Info'),
    ]

    recipient = models.ForeignKey(
        ClubMember, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title}"


# ==============================================================================
# CLUB APPLICATION — "Join the Club" form submissions
# ==============================================================================

class ClubApplication(models.Model):
    """
    Stores 'Join the Club' applications from prospective members.
    Club Head reviews and approves/rejects from the admin dashboard.
    On approval, a ClubMember record is auto-created.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    BRANCH_CHOICES = [
        ('ece', 'Electronics & Communication Engineering (ECE)'),
        ('cse', 'Computer Science & Engineering (CSE)'),
        ('iot', 'Internet of Things (IoT)'),
        ('me', 'Mechanical Engineering'),
        ('ce', 'Civil Engineering'),
        ('ee', 'Electrical Engineering'),
        ('other', 'Other'),
    ]

    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    ]

    DOMAIN_CHOICES = [
        ('electronics_iot', '⚙️ Core Electronics & IoT'),
        ('software_web', '💻 Software & Web Development'),
        ('robotics', '🤖 Robotics & Autonomous Systems'),
        ('uiux_content', '🎨 UI/UX Design & Content Management'),
    ]

    SKILL_CHOICES = [
        ('beginner', 'Absolute Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    rit_email_validator = RegexValidator(
        regex=r'^.+@ritroorkee\.com$',
        message='Only @ritroorkee.com email addresses are allowed.',
    )

    # --- Linked User (if logged in during submission) ---
    user = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='club_applications',
        help_text="Django user who submitted this application (if logged in)"
    )

    # --- Section 1: Basic Identity ---
    full_name = models.CharField(max_length=200, help_text="Full name of the applicant")
    profile_photo = models.ImageField(upload_to='application_photos/', null=True, blank=True, help_text="Professional profile photo")
    resume = models.FileField(upload_to='application_resumes/', storage=RawMediaCloudinaryStorage(), null=True, blank=False, help_text="Resume (PDF)")
    email = models.EmailField(
        unique=True,
        db_index=True,
        validators=[rit_email_validator],
        help_text="College email (must end with @ritroorkee.com)"
    )
    personal_email = models.EmailField(
        unique=True,
        db_index=True,
        null=True, blank=False,
        help_text="Personal Gmail ID (used for website login)"
    )
    whatsapp_number = models.CharField(max_length=15, help_text="WhatsApp number for team communication")
    roll_number = models.CharField(max_length=30, unique=True, help_text="College roll number")

    # --- Section 2: Academic & Club Fit ---
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES)
    current_year = models.CharField(max_length=5, choices=YEAR_CHOICES)
    domain_of_interest = models.CharField(max_length=30, choices=DOMAIN_CHOICES)

    # --- Section 3: Tech Skills & Motivation ---
    skill_level = models.CharField(max_length=20, choices=SKILL_CHOICES)
    motivation = models.TextField(help_text="Why do you want to join CECP?")
    quote = models.CharField(max_length=255, blank=True, help_text="Your personal quote or signature phrase")
    github_url = models.URLField(blank=True, help_text="GitHub profile (optional)")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile (optional)")

    # --- Status & Review ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    assigned_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='member',
        help_text="Category on the public Team page"
    )
    assigned_role = models.CharField(
        max_length=100,
        null=True, blank=True,
        help_text="Specific role/title (e.g., Web Master, Hardware Lead)"
    )
    reviewed_by = models.ForeignKey(
        ClubMember, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_applications',
        help_text="Club Head who reviewed this application"
    )
    rejection_reason = models.TextField(blank=True)
    send_notification_email = models.BooleanField(
        default=False,
        help_text="Check this box and save to manually trigger an email notification based on the current status."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Club Application'
        verbose_name_plural = 'Club Applications'

    def __str__(self):
        return f"{self.full_name} ({self.email}) — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        is_newly_approved = False
        if self.pk:
            old_instance = ClubApplication.objects.get(pk=self.pk)
            if old_instance.status != 'approved' and self.status == 'approved':
                is_newly_approved = True
        elif self.status == 'approved':
            is_newly_approved = True

        super().save(*args, **kwargs)

        if is_newly_approved:
            from django.contrib.auth.models import User
            # Find or create user using personal_email (for Google login linking)
            user = self.user
            target_email = self.personal_email or self.email
            if not user and target_email:
                user = User.objects.filter(email__iexact=target_email).first()
            if not user and target_email:
                # Create user
                base_username = target_email.split('@')[0]
                # Ensure unique username
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=target_email,
                    first_name=self.full_name.split()[0] if self.full_name else '',
                    last_name=' '.join(self.full_name.split()[1:]) if self.full_name and len(self.full_name.split()) > 1 else ''
                )
                self.user = user
                self.save(update_fields=['user'])
            
            # Sync to ClubMember
            member, _ = ClubMember.objects.get_or_create(user=user)
            member.display_name = self.full_name
            if self.assigned_category:
                member.category = self.assigned_category
            if self.assigned_role:
                member.display_role = self.assigned_role
            if self.profile_photo:
                # Properly link the exact same file path so it doesn't break
                member.profile_image.name = self.profile_photo.name
            if getattr(self, 'quote', None):
                member.quote = self.quote
            if getattr(self, 'github_url', None):
                member.github_url = self.github_url
            if getattr(self, 'linkedin_url', None):
                member.linkedin_url = self.linkedin_url
            member.save()
            
            # Sync to UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if self.github_url:
                profile.github_profile = self.github_url
            if self.linkedin_url:
                profile.linkedin_profile = self.linkedin_url
            profile.save()


# ==============================================================================
# INITIATIVE — Preserved from original
# ==============================================================================

class Initiative(models.Model):
    """Represents a core initiative/vertical of the CECP club."""
    title = models.CharField(max_length=200, help_text="Initiative title")
    description = models.TextField(help_text="Detailed description of the initiative")
    icon_class = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Initiatives'

    def __str__(self):
        return self.title


# ==============================================================================
# USER PROFILE
# ==============================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]

    COURSE_CHOICES = [
        ('B.Tech', 'B.Tech'),
        ('MBA', 'MBA'),
        ('BBA', 'BBA'),
        ('BCA', 'BCA'),
        ('MCA', 'MCA'),
        ('M.Tech', 'M.Tech'),
    ]
    BRANCH_CHOICES = [
        ('ECE', 'Electronics and Communication Engineering (ECE)'),
        ('CSE', 'Computer Science (CSE)'),
        ('AI/ML', 'Artificial Intelligence (AI/ML)'),
        ('CE', 'Civil Engineering (CE)'),
        ('IT', 'Information Technology (IT)'),
        ('EE', 'Electrical Engineering (EE)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    course = models.CharField(max_length=20, choices=COURSE_CHOICES, blank=True, null=True)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES, blank=True, null=True, help_text="Only applicable for B.Tech")
    graduation_year = models.CharField(max_length=9, blank=True, null=True, help_text="e.g., 2025-2029")
    college_roll_number = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    hometown = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Patna, Bihar")
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    github_profile = models.URLField(max_length=200, blank=True, null=True)
    linkedin_profile = models.URLField(max_length=200, blank=True, null=True)
    quote = models.CharField(
        max_length=100, blank=True, null=True,
        help_text='Your personal quote'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)
# ==============================================================================
# BLOG - Articles and Research
# ==============================================================================

class Blog(models.Model):
    title = models.CharField(max_length=200, help_text="Blog title")
    content = models.TextField(help_text="Blog content")
    image = models.ImageField(upload_to="blogs/", blank=True, null=True, help_text="Cover image")
    category_tag = models.CharField(max_length=50, blank=True, help_text="e.g., AI & Vision")
    read_time = models.CharField(max_length=50, default="5 min read", blank=True)
    author = models.ForeignKey(
        ClubMember, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="blogs"
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# ==============================================================================
# EVENT
# ==============================================================================

class Event(models.Model):
    EVENT_TYPES = [
        ('Hackathon', 'Hackathon'),
        ('Workshop', 'Workshop'),
        ('Competition', 'Competition'),
        ('Talk', 'Talk'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Live Now', 'Live Now'),
        ('Completed', 'Completed'),
        ('Ongoing', 'Ongoing'),
    ]

    title = models.CharField(max_length=200, help_text='Event title')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='Other')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Upcoming')
    description = models.TextField(help_text='Brief event description')
    date_range = models.CharField(max_length=100, help_text='e.g., 24-26 May 2025')
    location = models.CharField(max_length=200, help_text='e.g., CECP, Bhopal')
    image = models.ImageField(upload_to='events/', blank=True, null=True, help_text='Event cover image')
    is_featured = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, help_text='Registration or View Details URL')
    action_text = models.CharField(max_length=50, default='Register Now', help_text='Text for the button (e.g., Register Now, View Details, View Highlights)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
