# ==============================================================================
# Landing App — Views
# ==============================================================================
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q

from .models import (
    Project, Initiative, ClubMember, ProjectCategory, Notification,
    ClubApplication
)
from .supabase_client import fetch_initiatives, fetch_featured_projects
from .forms import UnifiedLoginForm, ProjectSubmissionForm, UserRegistrationForm, ClubApplicationForm
from .services import categorize_project_level

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
    ).select_related('category', 'submitted_by').prefetch_related('team_members')

    categories = ProjectCategory.objects.annotate(
        project_count=Count('projects', filter=Q(projects__approval_status='approved'))
    )

    stats = {
        'total_projects': Project.objects.filter(approval_status='approved').count(),
        'active_members': ClubMember.objects.filter(is_active=True).count(),
        'categories': ProjectCategory.objects.count(),
    }

    team_members = ClubMember.objects.filter(is_active=True).select_related('user').order_by('category', 'user__first_name')

    user_application = None
    if request.user.is_authenticated:
        # Tier 1: Direct FK link
        user_application = ClubApplication.objects.filter(user=request.user).first()
        # Tier 2: Email match
        if not user_application and request.user.email:
            user_application = ClubApplication.objects.filter(email__iexact=request.user.email).first()
            if user_application and not user_application.user:
                user_application.user = request.user
                user_application.save(update_fields=['user'])
    if not user_application:
        # Tier 3: Session cookie
        session_email = request.session.get('applied_email')
        if session_email:
            user_application = ClubApplication.objects.filter(email__iexact=session_email).first()

    context = {
        'initiatives': initiatives,
        'projects': approved_projects,
        'categories': categories,
        'stats': stats,
        'team_members': team_members,
        'user_application': user_application,
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
                        display_name = profile.display_name
                    elif profile.role == 'member' and profile.is_active:
                        role = 'core_member'
                        display_name = profile.display_name
                    else:
                        role = 'core_member'
                        display_name = profile.display_name
                except Exception:
                    role = 'general'

            # Store in session
            request.session['user_role'] = role
            request.session['display_name'] = display_name
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
    project = get_object_or_404(Project, id=project_id, approval_status='approved')
    return render(request, 'landing/project_detail.html', {
        'project': project,
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
        my_projects = Project.objects.filter(submitted_by=member).select_related('category').order_by('-created_at')
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
        'page_title': f'Dashboard — {member.display_name if member else request.user.username}',
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

    my_projects = Project.objects.filter(submitted_by=member).select_related('category').order_by('-created_at')
    notifications = Notification.objects.filter(recipient=member, is_read=False)[:10]
    pending_count = Project.objects.filter(approval_status='pending').count() if member.can_approve_projects else 0

    context = {
        'member': member,
        'is_club_member': True,
        'my_projects': my_projects,
        'notifications': notifications,
        'pending_count': pending_count,
        'page_title': f'Dashboard — {member.display_name}',
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
            project.tech_stack = form.cleaned_data.get('tech_stack_input', [])
            if project.spec:
                project.level = categorize_project_level(project.spec)
            if member.can_approve_projects:
                project.approval_status = 'approved'
                project.approved_by = member
                messages.success(request, f'Project "{project.title}" published!')
            else:
                project.approval_status = 'pending'
                messages.success(request, f'Project "{project.title}" submitted for review!')
                _notify_club_heads(project, member)
            project.save()
            project.team_members.add(member)
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
            if project.submitted_by == member or member.can_approve_projects:
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


@login_required(login_url='/login/')
@require_POST
def approve_project(request, project_id):
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        return JsonResponse({'error': 'No club profile'}, status=403)
    if not member.can_approve_projects:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    project = get_object_or_404(Project, id=project_id, approval_status='pending')
    project.approval_status = 'approved'
    project.approved_by = member
    project.save()

    if project.submitted_by:
        Notification.objects.create(
            recipient=project.submitted_by, notification_type='approved',
            title=f'Project Approved: {project.title}',
            message=f'Your project "{project.title}" has been approved by {member.display_name}!',
            related_project=project,
        )
    return JsonResponse({'status': 'approved', 'project_id': project_id})


@login_required(login_url='/login/')
@require_POST
def reject_project(request, project_id):
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        return JsonResponse({'error': 'No club profile'}, status=403)
    if not member.can_approve_projects:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    project = get_object_or_404(Project, id=project_id, approval_status='pending')
    reason = request.POST.get('reason', 'No reason provided')
    project.approval_status = 'rejected'
    project.rejection_reason = reason
    project.approved_by = member
    project.save()

    if project.submitted_by:
        Notification.objects.create(
            recipient=project.submitted_by, notification_type='rejected',
            title=f'Project Rejected: {project.title}',
            message=f'Your project "{project.title}" was not approved. Reason: {reason}',
            related_project=project,
        )
    return JsonResponse({'status': 'rejected', 'project_id': project_id})


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
            message=f'{submitter.display_name} submitted "{project.title}" for review.',
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
        app = ClubApplication.objects.filter(email__iexact=request.user.email, status='approved').first()
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

    return render(request, 'landing/profile.html', {
        'page_title': 'My Profile — CECP',
        'profile': profile,
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
        
    return render(request, 'landing/edit_profile.html', {
        'page_title': 'Edit Profile — CECP',
        'form': form,
        'profile': profile,
    })

def team_view(request):
    # ==================================================================
    # Single queryset — filtered into 4 context buckets.
    # select_related('user') avoids N+1 on display_name / get_full_name.
    # ==================================================================
    active_members = (
        ClubMember.objects.filter(is_active=True)
        .select_related('user')
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
