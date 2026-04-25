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
    Project, Initiative, ClubMember, ProjectCategory, Notification, TeamMember
)
from .supabase_client import fetch_initiatives, fetch_featured_projects
from .forms import UnifiedLoginForm, ProjectSubmissionForm
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

    team_members = TeamMember.objects.filter(is_active=True).order_by('display_order')

    context = {
        'initiatives': initiatives,
        'projects': approved_projects,
        'categories': categories,
        'stats': stats,
        'team_members': team_members,
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
