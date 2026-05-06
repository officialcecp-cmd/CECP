# ==============================================================================
# Landing App — Views
# ==============================================================================
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q

from .models import (
    Project, Initiative, ClubMember, ProjectCategory, Notification,
    ClubApplication, Blog
)
from .supabase_client import fetch_initiatives, fetch_featured_projects
from .forms import UnifiedLoginForm, ProjectSubmissionForm, UserRegistrationForm, ClubApplicationForm, ClubApplicationReviewForm
from .services import categorize_project_level


def is_admin(user):
    """Returns True if user is a superuser or in CECP_Admins group."""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='CECP_Admins').exists())

def ping(request):
    """Keep-alive endpoint for Vercel Serverless to prevent cold starts."""
    return JsonResponse({"status": "warm", "message": "CECP Server is alive"})

logger = logging.getLogger(__name__)

FALLBACK_INITIATIVES = [
    {'title': 'Embedded Systems & Defense Tech', 'description': 'Prototyping advanced hardware controllers, IoT architectures, and sensor integration using ESP32, NodeMCU, and Arduino.', 'icon': 'chip'},
    {'title': 'AI & Computer Vision', 'description': 'Developing intelligent software pipelines using Python, OpenCV, and YOLO models for object detection and automation.', 'icon': 'eye'},
    {'title': 'Hackathons & Open Source', 'description': 'Competing in national-level technical symposiums, Buildathons, and contributing to open-source engineering.', 'icon': 'code'},
]


# ==============================================================================
# 1. LANDING PAGE
# ==============================================================================

def index(request):
    initiatives = fetch_initiatives()
    if initiatives is None:
        initiatives = FALLBACK_INITIATIVES

    approved_projects = Project.objects.filter(
        approval_status='approved'
    ).select_related('category', 'submitted_by', 'project_lead', 'project_lead__user').prefetch_related('team_members', 'achievements')

    categories = ProjectCategory.objects.annotate(
        project_count=Count('projects', filter=Q(projects__approval_status='approved'))
    )
    
    # Strictly filter active members to those with approved apps or manual admins
    approved_apps = ClubApplication.objects.filter(status='approved')
    approved_users = approved_apps.exclude(user__isnull=True).values('user')
    approved_emails = approved_apps.values('email')
    valid_member_filter = Q(user__in=approved_users) | Q(user__email__in=approved_emails) | Q(category__in=['advisor', 'head'])

    stats = {
        'total_projects': Project.objects.filter(approval_status='approved').count(),
        'active_members': ClubMember.objects.filter(is_active=True).filter(valid_member_filter).exclude(category='advisor').count(),
        'categories': ProjectCategory.objects.count(),
    }

    team_members = ClubMember.objects.filter(is_active=True).filter(valid_member_filter).select_related('user', 'user__profile').order_by('category', 'user__first_name')

    user_application = None
    if request.user.is_authenticated:
        # Tier 1: Direct FK link
        user_application = ClubApplication.objects.filter(user=request.user).first()
        # Tier 2: Email match
        if not user_application and request.user.email:
            user_application = ClubApplication.objects.filter(Q(email__iexact=request.user.email) | Q(personal_email__iexact=request.user.email)).first()
            if user_application and not user_application.user:
                user_application.user = request.user
                user_application.save(update_fields=['user'])
    if not user_application:
        # Tier 3: Session cookie
        session_email = request.session.get('applied_email')
        if session_email:
            user_application = ClubApplication.objects.filter(email__iexact=session_email).first()

    approved_blogs = Blog.objects.filter(is_approved=True).select_related('author', 'author__user').order_by('-created_at')[:10]
    is_cecp_team = False
    if request.user.is_authenticated:
        is_cecp_team = request.user.is_superuser or request.user.groups.filter(name='CECP_Team').exists()

    context = {
        'initiatives': initiatives,
        'projects': approved_projects,
        'categories': categories,
        'stats': stats,
        'team_members': team_members,
        'user_application': user_application,
        'blogs': approved_blogs,
        'is_cecp_team': is_cecp_team,
        'page_title': 'CECP — Centre for Electronics & Coding Projects',
    }
    return render(request, 'landing/index.html', context)


# ==============================================================================
# 2. UNIFIED LOGIN — Single form, role-based routing
# ==============================================================================

def auth_portal(request):
    """
    Unified login page. Single email/username + password form.
    After auth, determines role and routes accordingly:
      - Admin (hod/faculty/club_head) → admin dashboard
      - Core Member → welcome popup → member dashboard
      - General User → limited dashboard
    """
    if request.user.is_authenticated:
        return _route_by_role(request)

    if request.method == 'POST':
        form = UnifiedLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Determine role from ClubMember profile
            if user.is_superuser:
                role = 'superuser'
                display_name = "Master Admin"
            else:
                role = 'general'
                display_name = user.get_full_name() or user.username
                try:
                    profile = user.club_profile
                    if profile.role in ('hod', 'faculty', 'club_head'):
                        role = 'admin'
                        display_name = profile.get_display_name
                    elif profile.role == 'member' and profile.is_active:
                        role = 'core_member'
                        display_name = profile.get_display_name
                    else:
                        role = 'core_member'
                        display_name = profile.get_display_name
                except Exception:
                    role = 'general'

            # Store in session
            request.session['user_role'] = role
            request.session['get_display_name'] = display_name
            request.session['login_type'] = role

            # Handle remember me
            if not request.POST.get('remember'):
                request.session.set_expiry(0)  # Browser close = logout

            if role == 'superuser':
                messages.success(request, 'Welcome to the Master Dashboard!')
                return redirect('/admin/')
            elif role == 'admin':
                messages.success(request, f'Welcome back, {display_name}!')
                return redirect('landing:index')
            elif role == 'core_member':
                messages.success(request, f'Welcome, {display_name}!')
                return redirect('landing:index')
            else:
                messages.success(request, f'Welcome, {display_name}!')
                return redirect('landing:index')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = UnifiedLoginForm()

    return render(request, 'landing/auth_portal.html', {
        'login_form': form,
        'page_title': 'Login — CECP Access Portal',
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('landing:index')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # Use email as username
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Note: The post_save signal in signals.py automatically creates the ClubMember
            # profile with role='member' for this new user.
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('landing:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'landing/register.html', {
        'register_form': form,
        'page_title': 'Join CECP Club',
    })


def _route_by_role(request):
    """Route authenticated users based on their session role."""
    if request.user.is_superuser:
        return redirect('/admin/')
    role = request.session.get('user_role', 'general')
    if role == 'admin':
        return redirect('landing:dashboard')
    return redirect('landing:member_dashboard')


def member_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing:index')


def project_detail(request, project_id):
    # Allow admins to preview pending projects; public only sees approved ones
    if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='CECP_Admins').exists()):
        project = get_object_or_404(Project, id=project_id)
    else:
        project = get_object_or_404(Project, id=project_id, approval_status='approved')
    
    achievements = project.achievements.all()
    team = project.team_members.select_related('user', 'user__profile').all()
    
    return render(request, 'landing/project_detail.html', {
        'project': project,
        'achievements': achievements,
        'team': team,
        'page_title': f"{project.title} — CECP",
    })


# ==============================================================================
# 3. MEMBER DASHBOARD
# ==============================================================================

@login_required(login_url='/login/')
def member_dashboard(request):
    try:
        member = request.user.club_profile
        is_club_member = True
    except Exception:
        member = None
        is_club_member = False

    if member:
        my_projects = Project.objects.filter(
            Q(submitted_by=member) | Q(team_members=member)
        ).distinct().select_related('category', 'project_lead', 'project_lead__user').prefetch_related('achievements').order_by('-created_at')
        notifications = Notification.objects.filter(recipient=member, is_read=False)[:10]
        pending_count = Project.objects.filter(approval_status='pending').count() if member.can_approve_projects else 0
    else:
        my_projects = []
        notifications = []
        pending_count = 0

    context = {
        'member': member,
        'is_club_member': is_club_member,
        'my_projects': my_projects,
        'notifications': notifications,
        'pending_count': pending_count,
        'total_approved': Project.objects.filter(approval_status='approved').count(),
        'page_title': f'Dashboard — {member.get_display_name if member else request.user.username}',
    }
    return render(request, 'landing/dashboard.html', context)


# ==============================================================================
# 4. ADMIN DASHBOARD
# ==============================================================================

@login_required(login_url='/login/')
def dashboard(request):
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        messages.error(request, 'Your account is not linked to a club member profile.')
        return redirect('landing:index')

    my_projects = Project.objects.filter(
        Q(submitted_by=member) | Q(team_members=member)
    ).distinct().select_related('category', 'project_lead', 'project_lead__user').prefetch_related('achievements').order_by('-created_at')
    notifications = Notification.objects.filter(recipient=member, is_read=False)[:10]
    pending_count = Project.objects.filter(approval_status='pending').count() if member.can_approve_projects else 0

    context = {
        'member': member,
        'is_club_member': True,
        'my_projects': my_projects,
        'notifications': notifications,
        'pending_count': pending_count,
        'page_title': f'Dashboard — {member.get_display_name}',
    }
    return render(request, 'landing/dashboard.html', context)


# ==============================================================================
# 5. PROJECT SUBMISSION
# ==============================================================================

@login_required(login_url='/login/')
def submit_project(request):
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        messages.error(request, 'Your account is not linked to a club member profile.')
        return redirect('landing:index')

    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.submitted_by = member
            project.project_lead = member
            project.tech_stack = form.cleaned_data.get('tech_stack_input', [])
            if project.spec:
                project.level = categorize_project_level(project.spec)
            if member.can_approve_projects:
                project.approval_status = 'approved'
                project.is_approved = True
                project.approved_by = member
                messages.success(request, f'Project "{project.title}" published!')
            else:
                project.approval_status = 'pending'
                messages.success(request, f'Project "{project.title}" submitted for review!')
            project.save()

            # --- Add the submitter as a team member ---
            project.team_members.add(member)

            # --- Link team members by email / name ---
            team_data = form.cleaned_data.get('team_members_json', [])
            external_teammates = []
            from django.contrib.auth.models import User as DjangoUser
            from landing.models import ClubApplication

            for tm in team_data:
                email = tm['email']
                name = tm['name']
                user = DjangoUser.objects.filter(email__iexact=email).first()
                if not user:
                    app = ClubApplication.objects.filter(personal_email__iexact=email, status='approved').first()
                    if app and app.user:
                        user = app.user
                
                if user:
                    try:
                        team_member = user.club_profile
                        project.team_members.add(team_member)
                        Notification.objects.create(
                            recipient=team_member,
                            notification_type='info',
                            title=f'Added to Project: {project.title}',
                            message=f'{member.get_display_name} added you as a team member on "{project.title}".',
                            related_project=project,
                        )
                    except ClubMember.DoesNotExist:
                        external_teammates.append({'name': name or email, 'email': email})
                else:
                    external_teammates.append({'name': name or email, 'email': email})
            
            if external_teammates:
                project.external_team_members = external_teammates
                project.save()

            # --- Create achievements ---
            achievements_data = form.cleaned_data.get('achievements_json', [])
            from landing.models import ProjectAchievement
            from datetime import datetime
            for ach in achievements_data:
                try:
                    ach_date = datetime.strptime(ach['date'], '%Y-%m-%d').date()
                    achievement_obj = ProjectAchievement.objects.create(
                        project=project,
                        title=ach['title'],
                        achievement_type=ach.get('achievement_type', 'competition'),
                        event_name=ach.get('event_name', ''),
                        position=ach.get('position', ''),
                        description=ach.get('description', ''),
                        date=ach_date,
                        certificate_url=ach.get('certificate_url', ''),
                    )
                    # Check for uploaded file if ID was passed
                    ach_id = ach.get('id')
                    if ach_id:
                        cert_file = request.FILES.get(f'achievement_cert_{ach_id}')
                        if cert_file:
                            achievement_obj.certificate_file = cert_file
                            achievement_obj.save()
                except (ValueError, KeyError):
                    continue

            if project.approval_status == 'pending':
                _notify_club_heads(project, member)
            return redirect('landing:dashboard')
    else:
        form = ProjectSubmissionForm()

    return render(request, 'landing/submit_project.html', {
        'form': form, 'member': member,
        'page_title': 'Submit Project — CECP',
    })


@login_required(login_url='/login/')
def delete_project(request, project_id):
    if request.method == 'POST':
        try:
            member = ClubMember.objects.get(user=request.user)
            project = get_object_or_404(Project, id=project_id)
            if project.submitted_by == member or project.project_lead == member or member.can_approve_projects:
                project.delete()
                messages.success(request, 'Project successfully deleted.')
            else:
                messages.error(request, 'You do not have permission to delete this project.')
        except ClubMember.DoesNotExist:
            messages.error(request, 'Member profile not found.')
    return redirect('landing:dashboard')


# ==============================================================================
# 6. APPROVAL DASHBOARD
# ==============================================================================

@login_required(login_url='/login/')
def approval_dashboard(request):
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        return redirect('landing:index')
    if not member.can_approve_projects:
        messages.error(request, 'Permission denied.')
        return redirect('landing:dashboard')

    pending_projects = Project.objects.filter(
        approval_status='pending'
    ).select_related('submitted_by', 'category').order_by('-created_at')

    return render(request, 'landing/approvals.html', {
        'member': member, 'pending_projects': pending_projects,
        'page_title': 'Approval Dashboard — CECP',
    })


@user_passes_test(is_admin, login_url='/login/')
@require_POST
def approve_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.approval_status = 'approved'
    project.is_approved = True
    project.save()

    # Send notification to ALL team members (including submitter)
    try:
        notified = set()
        for team_member in project.team_members.all():
            if team_member.id not in notified:
                Notification.objects.create(
                    recipient=team_member, notification_type='approved',
                    title=f'Project Approved: {project.title}',
                    message=f'Your project "{project.title}" has been approved and is now live on the CECP website!',
                    related_project=project,
                )
                notified.add(team_member.id)
        # Also notify submitter if not already in team
        if project.submitted_by and project.submitted_by.id not in notified:
            Notification.objects.create(
                recipient=project.submitted_by, notification_type='approved',
                title=f'Project Approved: {project.title}',
                message=f'Your project "{project.title}" has been approved and is now live!',
                related_project=project,
            )
    except Exception:
        pass

    messages.success(request, f'Project "{project.title}" has been approved and published.')
    return redirect('landing:moderator_dashboard')


@user_passes_test(is_admin, login_url='/login/')
@require_POST
def reject_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    title = project.title
    project.delete()
    messages.success(request, f'Project "{title}" has been rejected and removed.')
    return redirect('landing:moderator_dashboard')


@login_required(login_url='/login/')
@require_POST
def mark_notification_read(request, notification_id):
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        return JsonResponse({'error': 'No club profile'}, status=403)
    notification = get_object_or_404(Notification, id=notification_id, recipient=member)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})


# ==============================================================================
# 8. JOIN THE CLUB — Application Form
# ==============================================================================

def apply_view(request):
    """
    Public application form for prospective CECP members.
    No login required — anyone with a @ritroorkee.com email can apply.
    """
    has_applied = False
    application_status = None

    # Check if user already applied — 3-tier lookup:
    # 1. Direct user FK (permanent, survives session expiry)
    # 2. Auth email match (fallback)
    # 3. Session cookie (for anonymous users)
    existing_app = None
    
    if request.user.is_authenticated:
        # Tier 1: Direct FK link (most reliable)
        existing_app = ClubApplication.objects.filter(user=request.user).first()
        
        # Tier 2: Email match
        if not existing_app and request.user.email:
            existing_app = ClubApplication.objects.filter(email__iexact=request.user.email).first()
            # Auto-link for future lookups
            if existing_app and not existing_app.user:
                existing_app.user = request.user
                existing_app.save(update_fields=['user'])
    
    if not existing_app:
        # Tier 3: Session cookie (anonymous users)
        session_email = request.session.get('applied_email')
        if session_email:
            existing_app = ClubApplication.objects.filter(email__iexact=session_email).first()

    if existing_app:
        has_applied = True
        application_status = existing_app.get_status_display()

    if request.method == 'POST' and not has_applied:
        form = ClubApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            # Permanently link logged-in user to their application
            if request.user.is_authenticated:
                application.user = request.user
            application.save()
            # Also save to session as fallback for anonymous users
            request.session['applied_email'] = application.email
            
            # Notify Club Heads about the new application
            _notify_club_heads_application(application)
            messages.success(request, 'Your application has been submitted successfully! The Club Head will review it shortly.')
            return redirect('landing:apply')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClubApplicationForm()

    return render(request, 'landing/apply.html', {
        'form': form,
        'has_applied': has_applied,
        'application_status': application_status,
        'page_title': 'Apply to Join CECP Club',
    })


def apply_success_view(request):
    """Simple success page after application submission."""
    return render(request, 'landing/apply_success.html', {
        'page_title': 'Application Submitted — CECP',
    })


def delete_application(request):
    """Allow users to delete their pending or rejected application."""
    if request.method == 'POST':
        existing_app = None
        if request.user.is_authenticated:
            existing_app = ClubApplication.objects.filter(user=request.user).first()
            if not existing_app and request.user.email:
                existing_app = ClubApplication.objects.filter(email__iexact=request.user.email).first()
        if not existing_app:
            session_email = request.session.get('applied_email')
            if session_email:
                existing_app = ClubApplication.objects.filter(email__iexact=session_email).first()

        if existing_app:
            if existing_app.status != 'approved':
                # Delete the application
                existing_app.delete()
                # Clear session cookie if it exists
                if 'applied_email' in request.session:
                    del request.session['applied_email']
                messages.success(request, 'Your application has been successfully deleted.')
            else:
                messages.error(request, 'You cannot delete an approved application.')
        else:
            messages.error(request, 'No application found to delete.')
            
    return redirect('landing:apply')# ==============================================================================
# HELPERS
# ==============================================================================

def _notify_club_heads(project, submitter):
    heads = ClubMember.objects.filter(role__in=['club_head', 'hod'], is_active=True)
    for head in heads:
        Notification.objects.create(
            recipient=head, notification_type='submission',
            title=f'New Submission: {project.title}',
            message=f'{submitter.get_display_name} submitted "{project.title}" for review.',
            related_project=project,
        )


def _notify_club_heads_application(application):
    """Notify Club Heads about a new membership application."""
    heads = ClubMember.objects.filter(role__in=['club_head', 'hod'], is_active=True)
    for head in heads:
        Notification.objects.create(
            recipient=head, notification_type='info',
            title=f'New Application: {application.full_name}',
            message=(
                f'{application.full_name} ({application.email}) has applied to join CECP. '
                f'Branch: {application.get_branch_display()}, '
                f'Year: {application.get_current_year_display()}, '
                f'Domain: {application.get_domain_of_interest_display()}.'
            ),
        )

@login_required(login_url='/login/')
def profile_view(request):
    from landing.models import UserProfile, ClubApplication
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Auto-populate if freshly created
    if created and request.user.email:
        app = ClubApplication.objects.filter(Q(email__iexact=request.user.email) | Q(personal_email__iexact=request.user.email), status='approved').first()
        if app:
            profile.course = 'B.Tech'  # Default since CECP apps are primarily B.Tech
            profile.branch = app.branch
            profile.college_roll_number = app.roll_number
            profile.mobile_number = app.whatsapp_number
            profile.github_profile = app.github_url
            profile.linkedin_profile = app.linkedin_url
            if app.profile_photo:
                profile.profile_picture = app.profile_photo
            profile.save()
            
            # Sync name if user hasn't set it (from Google auth etc. it might already be set)
            if not request.user.first_name and not request.user.last_name and app.full_name:
                name_parts = app.full_name.split(' ', 1)
                request.user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    request.user.last_name = name_parts[1]
                request.user.save()

    # Determine if the user has an approved club application
    is_accepted = ClubApplication.objects.filter(
        user=request.user, status='approved'
    ).exists()
    if not is_accepted and request.user.email:
        is_accepted = ClubApplication.objects.filter(
            Q(email__iexact=request.user.email) | Q(personal_email__iexact=request.user.email), status='approved'
        ).exists()

    return render(request, 'landing/profile.html', {
        'page_title': 'My Profile — CECP',
        'profile': profile,
        'is_accepted': is_accepted,
    })

@login_required(login_url='/login/')
def edit_profile_view(request):
    from landing.models import UserProfile, ClubApplication
    from landing.forms import UserProfileForm
    from django.shortcuts import redirect
    from django.contrib import messages
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Auto-populate if freshly created
    if created and request.user.email:
        app = ClubApplication.objects.filter(email__iexact=request.user.email, status='approved').first()
        if app:
            profile.course = 'B.Tech'
            profile.branch = app.branch
            profile.college_roll_number = app.roll_number
            profile.mobile_number = app.whatsapp_number
            profile.github_profile = app.github_url
            profile.linkedin_profile = app.linkedin_url
            if app.profile_photo:
                profile.profile_picture = app.profile_photo
            profile.save()
            
            # Sync name if missing
            if not request.user.first_name and not request.user.last_name and app.full_name:
                name_parts = app.full_name.split(' ', 1)
                request.user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    request.user.last_name = name_parts[1]
                request.user.save()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('landing:profile')
    else:
        form = UserProfileForm(instance=profile)
        
    # Determine if the user has an approved club application
    is_accepted = ClubApplication.objects.filter(
        user=request.user, status='approved'
    ).exists()
    if not is_accepted and request.user.email:
        is_accepted = ClubApplication.objects.filter(
            email__iexact=request.user.email, status='approved'
        ).exists()

    return render(request, 'landing/edit_profile.html', {
        'page_title': 'Edit Profile — CECP',
        'form': form,
        'profile': profile,
        'is_accepted': is_accepted,
    })

def team_view(request):
    from .models import ClubApplication

    # Get approved applications' linked users and emails
    approved_apps = ClubApplication.objects.filter(status='approved')
    approved_users = approved_apps.exclude(user__isnull=True).values('user')
    approved_emails = approved_apps.values('email')

    # ==================================================================
    # Single queryset — filtered into 4 context buckets.
    # select_related('user') avoids N+1 on display_name / get_full_name.
    # Filters ONLY members who have an "Approved" application (or are Advisors/Heads).
    # ==================================================================
    active_members = (
        ClubMember.objects.filter(is_active=True)
        .filter(
            Q(user__in=approved_users) | 
            Q(user__email__in=approved_emails) |
            Q(category__in=['advisor', 'head'])
        )
        .select_related('user', 'user__profile')
        .order_by('user__first_name')
    )

    context = {
        'page_title': 'Our Team — CECP NEXUS',
        'advisors':        active_members.filter(category='advisor'),
        'club_heads':      active_members.filter(category='head'),
        'core_members':    active_members.filter(category='core'),
        'general_members': active_members.filter(category='member'),
    }
    return render(request, 'landing/team.html', context)


@login_required
def submit_blog(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='CECP_Team').exists()):
        messages.error(request, 'You are not authorized to submit blogs.')
        return redirect('landing:index')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_tag = request.POST.get('category_tag')
        read_time = request.POST.get('read_time') or '5 min read'
        image = request.FILES.get('image')

        author = ClubMember.objects.filter(user=request.user).first()

        blog = Blog.objects.create(
            title=title,
            content=content,
            category_tag=category_tag,
            read_time=read_time,
            image=image,
            author=author,
            is_approved=False
        )
        messages.success(request, 'Blog submitted successfully and is pending approval!')
        return redirect('landing:index')

    return render(request, 'landing/submit_blog.html')


def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    
    if not blog.is_approved:
        if not (request.user.is_superuser or request.user.groups.filter(name='CECP_Team').exists()):
            messages.error(request, 'This blog is pending approval and cannot be viewed yet.')
            return redirect('landing:index')

    context = {
        'blog': blog,
        'page_title': f"{blog.title} - CECP",
    }
    return render(request, 'landing/blog_detail.html', context)

@user_passes_test(is_admin, login_url='/login/')
def moderator_dashboard(request):
    pending_blogs = Blog.objects.filter(is_approved=False).order_by('-created_at')
    pending_apps = ClubApplication.objects.filter(status='pending').order_by('-created_at')
    pending_projects = Project.objects.filter(
        approval_status='pending'
    ).select_related('submitted_by', 'category').order_by('-created_at')
    return render(request, 'landing/moderator_dashboard.html', {
        'pending_blogs': pending_blogs,
        'pending_apps': pending_apps,
        'pending_projects': pending_projects,
        'page_title': 'Moderator Dashboard - CECP'
    })

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def approve_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    blog.is_approved = True
    blog.save()
    messages.success(request, f'Blog "{blog.title}" has been approved and published.')
    return redirect('landing:moderator_dashboard')

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def reject_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    blog.delete()
    messages.success(request, f'Blog "{blog.title}" has been rejected and deleted.')
    return redirect('landing:moderator_dashboard')

@user_passes_test(is_admin, login_url='/login/')
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.category_tag = request.POST.get('category_tag')
        if request.FILES.get('image'):
            blog.image = request.FILES.get('image')
        blog.save()
        messages.success(request, f'Blog "{blog.title}" has been updated.')
        return redirect('landing:moderator_dashboard')
    
    return render(request, 'landing/edit_blog.html', {'blog': blog, 'page_title': 'Edit Blog - CECP'})

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def accept_application(request, app_id):
    app = get_object_or_404(ClubApplication, id=app_id)
    app.status = 'approved'
    app.save()
    messages.success(request, f'Application for {app.full_name} has been approved.')
    return redirect('landing:moderator_dashboard')

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def reject_application(request, app_id):
    app = get_object_or_404(ClubApplication, id=app_id)
    app.status = 'rejected'
    app.save()
    messages.success(request, f'Application for {app.full_name} has been rejected.')
    return redirect('landing:moderator_dashboard')

@user_passes_test(is_admin, login_url='/login/')
def review_application(request, application_id):
    app = get_object_or_404(ClubApplication, id=application_id)
    if request.method == 'POST':
        form = ClubApplicationReviewForm(request.POST, instance=app)
        if form.is_valid():
            application = form.save(commit=False)
            try:
                member = request.user.club_profile
                application.reviewed_by = member
            except ClubMember.DoesNotExist:
                pass
            application.save()
            messages.success(request, f'Application for {application.full_name} has been reviewed and saved.')
            return redirect('landing:moderator_dashboard')
    else:
        form = ClubApplicationReviewForm(instance=app)
    
    return render(request, 'landing/review_application.html', {
        'form': form,
        'app': app,
        'page_title': f'Review Application: {app.full_name}'
    })


@user_passes_test(is_admin, login_url='/login/')
def download_resume(request, application_id):
    """
    Redirects to the Cloudinary URL for the resume.
    With RawMediaCloudinaryStorage, this correctly points to the raw pipeline.
    """
    app = get_object_or_404(ClubApplication, id=application_id)
    if not app.resume:
        raise Http404("No resume uploaded for this application.")

    return HttpResponseRedirect(app.resume.url)
