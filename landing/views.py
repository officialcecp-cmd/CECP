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
    ClubApplication, Blog, Event, EventStat, ProjectAccessRequest
)
from .supabase_client import fetch_initiatives, fetch_featured_projects
from .forms import UnifiedLoginForm, ProjectSubmissionForm, UserRegistrationForm, ClubApplicationForm, ClubApplicationReviewForm, PublicUserRegistrationForm
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
    events = Event.objects.all()
    event_stats = EventStat.objects.first()
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

    team_members = ClubMember.objects.filter(is_active=True).filter(valid_member_filter).select_related('user', 'user__profile').order_by('display_order', 'category', 'user__first_name')

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
    can_write_blog = False
    if request.user.is_authenticated:
        # Allow superusers, CECP_Team group, and any user with an active ClubMember profile
        can_write_blog = (
            request.user.is_superuser
            or request.user.groups.filter(name='CECP_Team').exists()
            or ClubMember.objects.filter(user=request.user, is_active=True).exists()
        )

    context = {
        'events': events,
        'event_stats': event_stats,
        'initiatives': initiatives,
        'projects': approved_projects,
        'featured_project': approved_projects.filter(is_featured=True).first(),
        'categories': categories,
        'stats': stats,
        'team_members': team_members,
        'user_application': user_application,
        'blogs': approved_blogs,
        'can_write_blog': can_write_blog,
        'is_application_open': True, # Or whatever it was supposed to be
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
                    if profile.role in ('hod', 'faculty', 'club_head') and profile.is_active:
                        role = 'admin'
                        display_name = profile.get_display_name
                    elif profile.is_active:
                        role = 'core_member'
                        display_name = profile.get_display_name
                    else:
                        # Inactive profile = public/visitor user
                        role = 'public'
                except Exception:
                    role = 'public'

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
    role = request.session.get('user_role', 'public')
    if role == 'admin':
        return redirect('landing:dashboard')
    elif role == 'core_member':
        return redirect('landing:member_dashboard')
    else:
        # Public/visitor users go to homepage
        return redirect('landing:index')


def member_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing:index')

def member_detail(request, member_id):
    member = get_object_or_404(ClubMember, id=member_id)
    # Fetch member projects
    projects = Project.objects.filter(Q(submitted_by=member) | Q(team_members=member), approval_status='approved').distinct().select_related('category').prefetch_related('achievements').order_by('-created_at')
    
    application = None
    if member.user:
        application = ClubApplication.objects.filter(user=member.user).first()
        if not application and member.user.email:
            application = ClubApplication.objects.filter(Q(email__iexact=member.user.email) | Q(personal_email__iexact=member.user.email)).first()

    return render(request, 'landing/member_detail.html', {
        'member': member,
        'application': application,
        'projects': projects,
        'page_title': f"{member.get_display_name} — CECP Profile",
    })

def project_detail(request, project_id):
    # Allow admins to preview pending projects; public only sees approved ones
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        project = get_object_or_404(
            Project.objects.select_related('category', 'submitted_by__user', 'project_lead__user'),
            id=project_id
        )
    else:
        project = get_object_or_404(
            Project.objects.select_related('category', 'submitted_by__user', 'project_lead__user'),
            id=project_id, approval_status='approved'
        )
    
    achievements = project.achievements.all()
    team = project.team_members.select_related('user', 'user__profile').all()
    external_team = project.external_team_members if isinstance(project.external_team_members, list) else []
    total_team_count = team.count() + len(external_team)

    # --- Access Control for project resources ---
    # Rule: Only ACTIVE club members (approved via ClubApplication), 
    # superusers, project team members, or users with approved access 
    # requests can see GitHub repos, docs, and PPT files.
    has_full_access = False
    access_request_status = None

    if request.user.is_authenticated:
        # Superusers and staff always have full access
        if request.user.is_superuser or request.user.is_staff:
            has_full_access = True
        else:
            # Check if user is an ACTIVE club member (approved via ClubApplication)
            try:
                member = request.user.club_profile
                if member.is_active:
                    has_full_access = True
            except ClubMember.DoesNotExist:
                pass

            # If still no access, check if user is a team member on THIS project
            if not has_full_access:
                if project.submitted_by and project.submitted_by.user_id == request.user.id:
                    has_full_access = True
                elif project.project_lead and project.project_lead.user_id == request.user.id:
                    has_full_access = True
                elif project.team_members.filter(user=request.user).exists():
                    has_full_access = True

            # If still no access, check for an approved access request
            if not has_full_access:
                access_req = ProjectAccessRequest.objects.filter(
                    requester=request.user, project=project
                ).only('status').first()
                if access_req:
                    access_request_status = access_req.status
                    if access_req.status == 'approved':
                        has_full_access = True
    
    return render(request, 'landing/project_detail.html', {
        'project': project,
        'achievements': achievements,
        'team': team,
        'total_team_count': total_team_count,
        'has_full_access': has_full_access,
        'access_request_status': access_request_status,
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
            try:
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
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Project save error: {e}")
                messages.error(request, f'Error during project submission: {str(e)}')
                return render(request, 'landing/submit_project.html', {'form': form, 'page_title': 'Submit Project'})

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
def edit_project(request, project_id):
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        messages.error(request, 'Your account is not linked to a club member profile.')
        return redirect('landing:index')

    project = get_object_or_404(Project, id=project_id)

    # Check permission
    if not (project.submitted_by == member or project.project_lead == member or member.can_approve_projects):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('landing:dashboard')

    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.tech_stack = form.cleaned_data.get('tech_stack_input', [])
            try:
                if project.spec:
                    project.level = categorize_project_level(project.spec)
                project.save()
            except Exception as e:
                messages.error(request, f'Error during project update: {str(e)}')
                return render(request, 'landing/edit_project.html', {'form': form, 'member': member, 'project': project, 'page_title': 'Edit Project'})

            # --- Update External Team Members ---
            team_data = form.cleaned_data.get('team_members_json', [])
            external_teammates = []
            from django.contrib.auth.models import User as DjangoUser
            from landing.models import ClubApplication

            # clear old team members except the lead
            project.team_members.clear()
            if project.project_lead:
                project.team_members.add(project.project_lead)
            if project.submitted_by:
                project.team_members.add(project.submitted_by)

            for tm in team_data:
                email = tm.get('email', '')
                name = tm.get('name', '')
                if not email:
                    continue
                user = DjangoUser.objects.filter(email__iexact=email).first()
                if not user:
                    app = ClubApplication.objects.filter(personal_email__iexact=email, status='approved').first()
                    if app and app.user:
                        user = app.user
                
                if user:
                    try:
                        team_member = user.club_profile
                        project.team_members.add(team_member)
                    except ClubMember.DoesNotExist:
                        external_teammates.append({'name': name or email, 'email': email})
                else:
                    external_teammates.append({'name': name or email, 'email': email})
            
            project.external_team_members = external_teammates
            project.save()

            # --- Update Achievements ---
            achievements_data = form.cleaned_data.get('achievements_json', [])
            from landing.models import ProjectAchievement
            from datetime import datetime
            
            # keep track of current achievements to delete removed ones
            current_achs = set(project.achievements.values_list('id', flat=True))
            processed_achs = set()

            for ach in achievements_data:
                try:
                    ach_date = datetime.strptime(ach['date'], '%Y-%m-%d').date()
                    # if ach has a numeric ID (and exists in DB), it's an update, else create
                    ach_id = ach.get('id')
                    try:
                        db_ach_id = int(ach_id)
                        if db_ach_id in current_achs:
                            achievement_obj = ProjectAchievement.objects.get(id=db_ach_id)
                            achievement_obj.title = ach['title']
                            achievement_obj.achievement_type = ach.get('achievement_type', 'competition')
                            achievement_obj.event_name = ach.get('event_name', '')
                            achievement_obj.position = ach.get('position', '')
                            achievement_obj.description = ach.get('description', '')
                            achievement_obj.date = ach_date
                            achievement_obj.certificate_url = ach.get('certificate_url', '')
                            achievement_obj.save()
                            processed_achs.add(db_ach_id)
                        else:
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
                    except (ValueError, TypeError):
                        # brand new
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
                    
                    # check for file upload
                    if ach_id:
                        cert_file = request.FILES.get(f"achievement_cert_{ach_id}")
                        if cert_file:
                            achievement_obj.certificate_file = cert_file
                            achievement_obj.save()

                except (ValueError, KeyError) as e:
                    continue

            # delete any achievements removed by the user
            to_delete = current_achs - processed_achs
            if to_delete:
                ProjectAchievement.objects.filter(id__in=to_delete).delete()

            messages.success(request, f'Project "{project.title}" has been updated!')
            return redirect('landing:dashboard')
    else:
        # Prepopulate dynamic fields
        import json
        team_members = project.external_team_members if isinstance(project.external_team_members, list) else []
        for tm in project.team_members.all():
            if tm != project.project_lead and tm != project.submitted_by:
                team_members.append({'name': tm.get_display_name, 'email': tm.user.email})
        
        achievements = []
        for ach in project.achievements.all():
            achievements.append({
                'id': ach.id,
                'title': ach.title,
                'event_name': ach.event_name,
                'achievement_type': ach.achievement_type,
                'position': ach.position,
                'date': ach.date.strftime('%Y-%m-%d') if ach.date else '',
                'certificate_url': ach.certificate_url,
                'has_file': bool(ach.certificate_file)
            })

        initial_data = {
            'tech_stack_input': ", ".join(project.tech_stack) if project.tech_stack else '',
            'team_members_json': json.dumps(team_members),
            'achievements_json': json.dumps(achievements),
        }
        form = ProjectSubmissionForm(instance=project, initial=initial_data)

    return render(request, 'landing/edit_project.html', {
        'form': form, 'member': member, 'project': project,
        'page_title': 'Edit Project — CECP',
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
    from landing.github_fetcher import sync_github_data
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

    # Fetch GitHub data (cached, refreshes every 6 hours)
    github_repos = []
    github_languages = {}
    if profile.github_profile:
        try:
            github_repos, github_languages = sync_github_data(profile)
        except Exception as e:
            logger.warning(f"GitHub sync failed for {request.user.username}: {e}")

    return render(request, 'landing/profile.html', {
        'page_title': 'My Profile — CECP',
        'profile': profile,
        'is_accepted': is_accepted,
        'github_repos': github_repos[:10],  # Top 10 repos
        'github_languages': github_languages,
        'github_languages_list': list(github_languages.keys())[:12],  # Top 12 languages
    })

@login_required(login_url='/login/')
@require_POST
def github_sync_view(request):
    """Force-refresh GitHub data for the logged-in user."""
    from landing.models import UserProfile
    from landing.github_fetcher import sync_github_data
    profile = UserProfile.objects.get(user=request.user)
    if not profile.github_profile:
        return JsonResponse({'error': 'No GitHub profile linked'}, status=400)
    try:
        repos, languages = sync_github_data(profile, force=True)
        return JsonResponse({
            'success': True,
            'repos_count': len(repos),
            'languages': list(languages.keys())[:12],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
        # ── Handle cropped base64 fallback (for browsers without DataTransfer) ──
        cropped_b64 = request.POST.get('profile_picture_cropped', '').strip()
        mutable_files = request.FILES.copy() if request.FILES else {}

        if cropped_b64 and 'profile_picture' not in request.FILES:
            import base64
            from django.core.files.base import ContentFile
            try:
                # Strip the data:image/...;base64, header
                header, data = cropped_b64.split(',', 1)
                img_data = base64.b64decode(data)
                mutable_files['profile_picture'] = ContentFile(img_data, name='profile_picture.jpg')
            except Exception:
                pass

        form = UserProfileForm(request.POST, mutable_files or request.FILES, instance=profile)
        if form.is_valid():
            saved_profile = form.save()

            # --- Sync profile_picture → ClubMember.profile_image ---
            # So that the public Team/Management cards always show the correct image.
            if saved_profile.profile_picture:
                try:
                    club_member = request.user.club_profile  # OneToOne related_name
                    if club_member.profile_image.name != saved_profile.profile_picture.name:
                        club_member.profile_image = saved_profile.profile_picture
                        club_member.save(update_fields=['profile_image'])
                except Exception:
                    pass  # User may not have a ClubMember record yet

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
        .order_by('display_order', 'user__first_name')
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
    # Allow superusers, CECP_Team group, and any user with an active ClubMember profile
    has_club_profile = ClubMember.objects.filter(user=request.user, is_active=True).exists()
    if not (request.user.is_superuser or request.user.groups.filter(name='CECP_Team').exists() or has_club_profile):
        messages.error(request, 'You are not authorized to submit blogs. Only club members can write blogs.')
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
        is_authorized = False
        if request.user.is_authenticated:
            try:
                profile = getattr(request.user, 'club_profile', None)
                is_authorized = (
                    request.user.is_superuser or 
                    request.user.groups.filter(name='CECP_Team').exists() or
                    (profile and blog.author == profile)
                )
            except Exception:
                pass

        if not is_authorized:
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


# ==============================================================================
# PUBLIC USER — Registration & Login
# ==============================================================================

def public_register_view(request):
    """Registration for public/visitor users. No club membership required."""
    if request.user.is_authenticated:
        return redirect('landing:index')

    if request.method == 'POST':
        form = PublicUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # Use email as username
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Log the user in immediately
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Mark session as public user
            request.session['user_role'] = 'public'
            request.session['login_type'] = 'public'
            request.session['display_name'] = user.get_full_name() or user.username

            messages.success(request, f'Welcome to CECP, {user.get_full_name()}! You can now explore projects and blogs.')
            return redirect('landing:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PublicUserRegistrationForm()

    return render(request, 'landing/public_register.html', {
        'form': form,
        'page_title': 'Create Account — CECP Visitor Portal',
    })


# ==============================================================================
# PROJECT ACCESS REQUEST — Request, Approve, Reject
# ==============================================================================

@login_required(login_url='/login/')
@require_POST
def request_project_access(request, project_id):
    """Public user requests access to a project's protected resources."""
    project = get_object_or_404(Project, id=project_id, approval_status='approved')

    # Check if user already has access (club member or team member)
    try:
        member = request.user.club_profile
        if member.is_active:
            messages.info(request, 'You already have full access as a club member.')
            return redirect('landing:project_detail', project_id=project_id)
    except ClubMember.DoesNotExist:
        pass

    # Check for existing request
    existing = ProjectAccessRequest.objects.filter(
        requester=request.user, project=project
    ).first()

    if existing:
        if existing.status == 'approved':
            messages.info(request, 'You already have access to this project.')
        elif existing.status == 'pending':
            messages.info(request, 'Your access request is already pending review.')
        elif existing.status == 'rejected':
            # Allow re-requesting after rejection
            existing.status = 'pending'
            existing.message = request.POST.get('message', '').strip()
            existing.save()
            messages.success(request, 'Your access request has been re-submitted.')
    else:
        ProjectAccessRequest.objects.create(
            requester=request.user,
            project=project,
            message=request.POST.get('message', '').strip(),
        )
        messages.success(request, f'Access request sent to the owner of "{project.title}". You will be notified when reviewed.')

        # Notify the project owner
        if project.project_lead:
            Notification.objects.create(
                recipient=project.project_lead,
                notification_type='info',
                title=f'Access Request: {project.title}',
                message=f'{request.user.get_full_name() or request.user.username} has requested access to your project "{project.title}" resources.',
                related_project=project,
            )
        elif project.submitted_by:
            Notification.objects.create(
                recipient=project.submitted_by,
                notification_type='info',
                title=f'Access Request: {project.title}',
                message=f'{request.user.get_full_name() or request.user.username} has requested access to your project "{project.title}" resources.',
                related_project=project,
            )

    return redirect('landing:project_detail', project_id=project_id)


@login_required(login_url='/login/')
def manage_access_requests(request):
    """Project owner views and manages incoming access requests."""
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        messages.error(request, 'You need a club member profile to manage access requests.')
        return redirect('landing:index')

    # Get projects owned by this user
    my_projects = Project.objects.filter(
        Q(submitted_by=member) | Q(project_lead=member)
    ).distinct()

    pending_requests = ProjectAccessRequest.objects.filter(
        project__in=my_projects, status='pending'
    ).select_related('requester', 'project').order_by('-created_at')

    all_requests = ProjectAccessRequest.objects.filter(
        project__in=my_projects
    ).select_related('requester', 'project').order_by('-created_at')[:50]

    return render(request, 'landing/access_requests.html', {
        'member': member,
        'pending_requests': pending_requests,
        'all_requests': all_requests,
        'page_title': 'Manage Access Requests — CECP',
    })


@login_required(login_url='/login/')
@require_POST
def approve_access_request(request, request_id):
    """Project owner approves an access request."""
    from django.utils import timezone
    access_req = get_object_or_404(ProjectAccessRequest, id=request_id)
    project = access_req.project

    # Verify the current user is the project owner
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        messages.error(request, 'Permission denied.')
        return redirect('landing:index')

    if not (project.submitted_by == member or project.project_lead == member or member.can_approve_projects):
        messages.error(request, 'You do not have permission to manage this project\'s access.')
        return redirect('landing:dashboard')

    access_req.status = 'approved'
    access_req.reviewed_by = request.user
    access_req.reviewed_at = timezone.now()
    access_req.save()

    messages.success(request, f'Access granted to {access_req.requester.get_full_name() or access_req.requester.username} for "{project.title}".')
    return redirect('landing:manage_access_requests')


@login_required(login_url='/login/')
@require_POST
def reject_access_request(request, request_id):
    """Project owner rejects an access request."""
    from django.utils import timezone
    access_req = get_object_or_404(ProjectAccessRequest, id=request_id)
    project = access_req.project

    # Verify the current user is the project owner
    try:
        member = request.user.club_profile
    except ClubMember.DoesNotExist:
        messages.error(request, 'Permission denied.')
        return redirect('landing:index')

    if not (project.submitted_by == member or project.project_lead == member or member.can_approve_projects):
        messages.error(request, 'You do not have permission to manage this project\'s access.')
        return redirect('landing:dashboard')

    access_req.status = 'rejected'
    access_req.reviewed_by = request.user
    access_req.reviewed_at = timezone.now()
    access_req.save()

    messages.success(request, f'Access denied for {access_req.requester.get_full_name() or access_req.requester.username}.')
    return redirect('landing:manage_access_requests')
