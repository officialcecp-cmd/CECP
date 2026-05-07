# ==============================================================================
# Landing App — Admin Configuration
# ==============================================================================
from django.contrib import admin
from .models import (
    Event, EventStat,
    Initiative, Project, ProjectAchievement,
    ClubMember, ProjectCategory, Notification, ClubApplication, Blog
)
from .services import categorize_project_level
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import format_html


# --- Club Member Admin --------------------------------------------------------

@admin.register(ClubMember)
class ClubMemberAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'member_id', 'role', 'category', 'display_role', 'display_order', 'is_active', 'joined_at')
    list_select_related = ('user',)
    list_editable = ('role', 'category', 'display_role', 'display_order', 'is_active')
    list_filter = ('role', 'category', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'member_id', 'display_role')
    raw_id_fields = ('user',)

    fieldsets = (
        ('User Account', {
            'fields': ('user', 'member_id', 'role', 'is_active', 'joined_at')
        }),
        ('Team Page Display', {
            'fields': ('display_order', 'category', 'display_role', 'display_name', 'profile_image', 'bio', 'quote'),
            'description': 'These fields control how the member appears on the public /team/ page.'
        }),
        ('Detailed Profile Info', {
            'fields': ('core_technologies', 'area_of_interest', 'experience'),
            'description': 'These fields are shown on the individual member profile detail page.'
        }),
        ('Contact & Social', {
            'fields': ('phone', 'linkedin_url', 'github_url'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        from .models import ClubApplication
        from django.db.models import Q
        
        # Get approved applications' linked users and emails
        approved_apps = ClubApplication.objects.filter(status='approved')
        approved_users = approved_apps.exclude(user__isnull=True).values('user')
        approved_emails = approved_apps.values('email')
        
        # Only show members who have an approved application OR are advisors/heads
        return qs.filter(
            Q(user__in=approved_users) | 
            Q(user__email__in=approved_emails) |
            Q(category__in=['advisor', 'head'])
        ).distinct()

    class Media:
        js = ('js/image_cropper.js',)


# --- Project Category Admin ---------------------------------------------------

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'display_order')
    list_editable = ('display_order',)
    prepopulated_fields = {'slug': ('name',)}


# --- Project Achievement Inline -----------------------------------------------

class ProjectAchievementInline(admin.TabularInline):
    model = ProjectAchievement
    extra = 0
    fields = ('title', 'achievement_type', 'event_name', 'position', 'date', 'certificate_url', 'certificate_file')


# --- Project Admin (with AI auto-categorization) ------------------------------

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'category', 'approval_status', 'status', 'submitted_by', 'project_lead', 'is_featured', 'year')
    list_select_related = ('submitted_by', 'submitted_by__user', 'category', 'approved_by', 'approved_by__user', 'project_lead', 'project_lead__user')
    list_editable = ('approval_status', 'is_featured')
    list_filter = ('approval_status', 'status', 'level', 'category', 'is_featured', 'year')
    search_fields = ('title', 'codename', 'description', 'spec')
    readonly_fields = ('level', 'created_at', 'updated_at')
    raw_id_fields = ('submitted_by', 'approved_by', 'project_lead')
    autocomplete_fields = ('team_members',)
    inlines = [ProjectAchievementInline]
    actions = ['approve_projects', 'reject_projects']

    fieldsets = (
        ('Project Info', {
            'fields': ('title', 'codename', 'description', 'image', 'category')
        }),
        ('Technical', {
            'fields': ('spec', 'tech_stack', 'level')
        }),
        ('Approval Workflow', {
            'fields': ('approval_status', 'submitted_by', 'approved_by', 'rejection_reason')
        }),
        ('Links', {
            'fields': ('github_url', 'demo_url', 'documentation_url', 'documentation_file', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Team & Display', {
            'fields': ('project_lead', 'team_members', 'status', 'is_featured', 'display_order', 'year')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # AI auto-categorization on spec change
        if obj.spec and (not obj.level or (change and 'spec' in form.changed_data)):
            obj.level = categorize_project_level(obj.spec)

        # Auto-approve when a superuser or staff adds a project via admin
        if not change and request.user.is_staff and obj.approval_status == 'pending':
            obj.approval_status = 'approved'

        super().save_model(request, obj, form, change)

    @admin.action(description='✅ Approve selected projects (publish to website)')
    def approve_projects(self, request, queryset):
        updated = queryset.update(approval_status='approved')
        self.message_user(request, f'{updated} project(s) approved and published to the website.')

    @admin.action(description='❌ Reject selected projects')
    def reject_projects(self, request, queryset):
        updated = queryset.update(approval_status='rejected')
        self.message_user(request, f'{updated} project(s) rejected.')


# --- Initiative Admin ---------------------------------------------------------

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_order', 'is_active', 'updated_at')
    list_editable = ('display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


# --- Notification Admin -------------------------------------------------------

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at',)


# --- Club Application Admin ---------------------------------------------------

@admin.register(ClubApplication)
class ClubApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'branch', 'current_year', 'domain_of_interest', 'skill_level', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'branch', 'current_year', 'domain_of_interest', 'skill_level')
    search_fields = ('full_name', 'email', 'roll_number', 'motivation')
    readonly_fields = ('photo_preview', 'created_at', 'updated_at', 'reviewed_by')
    actions = ['approve_applications', 'reject_applications']

    fieldsets = (
        ('Applicant Identity', {
            'fields': ('photo_preview', 'profile_photo', 'full_name', 'email', 'whatsapp_number', 'roll_number')
        }),
        ('Academic Info', {
            'fields': ('branch', 'current_year', 'domain_of_interest')
        }),
        ('Skills & Motivation', {
            'fields': ('skill_level', 'motivation', 'quote', 'github_url', 'linkedin_url')
        }),
        ('Review & Team Assignment', {
            'fields': ('status', 'assigned_category', 'assigned_role', 'reviewed_by', 'rejection_reason', 'send_notification_email'),
            'description': 'Set assigned_category and assigned_role before approving. A ClubMember record will be auto-created/updated.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def photo_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="120" height="120" style="border-radius: 8px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.3);" />', obj.profile_photo.url)
        return "No Photo Provided"
    photo_preview.short_description = 'Photo Preview'

    class Media:
        js = ('js/image_cropper.js',)

    def _sync_club_member(self, obj):
        """
        Core sync logic: when an application is approved, find or create
        the linked Django User and update/create their ClubMember record.
        """
        from django.contrib.auth.models import User as DjangoUser

        # Try to find the linked user by email
        user = obj.user
        if not user:
            try:
                user = DjangoUser.objects.get(email__iexact=obj.email)
            except DjangoUser.DoesNotExist:
                user = None

        if user:
            # Get or create the ClubMember for this user
            club_member, _ = ClubMember.objects.get_or_create(user=user)
            club_member.category = obj.assigned_category or 'member'
            club_member.display_role = obj.assigned_role or ''
            club_member.github_url = obj.github_url or ''
            club_member.linkedin_url = obj.linkedin_url or ''
            if obj.profile_photo and not club_member.profile_image:
                club_member.profile_image = obj.profile_photo
            club_member.is_active = True
            club_member.save()
            return club_member
        return None

    def save_model(self, request, obj, form, change):
        send_manual_email = form.cleaned_data.get('send_notification_email', False)

        # Auto-capture the logged-in admin reviewer
        if obj.status in ['approved', 'rejected']:
            if hasattr(request.user, 'club_profile'):
                obj.reviewed_by = request.user.club_profile
        elif obj.status == 'pending':
            obj.reviewed_by = None

        # CRITICAL: Reset the checkbox before saving
        if send_manual_email:
            obj.send_notification_email = False

        super().save_model(request, obj, form, change)

        # Sync ClubMember on approval
        if obj.status == 'approved':
            self._sync_club_member(obj)

        # Send Manual Email Notification
        if send_manual_email:
            try:
                admin_name = request.user.get_full_name() or request.user.username
                subject = f'CECP: Application {obj.get_status_display()}'

                context = {
                    'applicant_name': obj.full_name,
                    'status': obj.status,
                    'admin_name': admin_name
                }
                html_content = render_to_string('landing/emails/welcome_email.html', context)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=f"Hello {obj.full_name},\nYour application status is now: {obj.get_status_display()}.\nReviewed by: {admin_name}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[obj.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)
            except Exception as e:
                print(f"Error sending email to {obj.email}: {e}")

    @admin.action(description='✅ Approve selected applications')
    def approve_applications(self, request, queryset):
        reviewer = getattr(request.user, 'club_profile', None)
        if reviewer:
            queryset.update(status='approved', reviewed_by=reviewer)
        else:
            queryset.update(status='approved')

        synced = 0
        for obj in queryset:
            if self._sync_club_member(obj):
                synced += 1

        self.message_user(request, f'{queryset.count()} application(s) approved. {synced} ClubMember record(s) synced.')

    @admin.action(description='❌ Reject selected applications')
    def reject_applications(self, request, queryset):
        reviewer = getattr(request.user, 'club_profile', None)
        if reviewer:
            updated = queryset.update(status='rejected', reviewed_by=reviewer)
        else:
            updated = queryset.update(status='rejected')

        # Deactivate corresponding ClubMembers
        from django.contrib.auth.models import User as DjangoUser
        for obj in queryset:
            try:
                user = obj.user or DjangoUser.objects.get(email__iexact=obj.email)
                ClubMember.objects.filter(user=user).update(is_active=False)
            except DjangoUser.DoesNotExist:
                pass

        self.message_user(request, f'{updated} application(s) rejected.')

# --- Blog Admin ---------------------------------------------------------------

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category_tag', 'is_approved', 'created_at')
    list_select_related = ('author', 'author__user')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'category_tag')
    search_fields = ('title', 'content')
    
    @admin.action(description='\xe2\x9c\x85 Approve selected blogs')
    def approve_blogs(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='\xe2\x9d\x8c Reject selected blogs')
    def reject_blogs(self, request, queryset):
        queryset.update(is_approved=False)
        
    actions = ['approve_blogs', 'reject_blogs']


# --- Event Admin --------------------------------------------------------------

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'status', 'date_range', 'is_featured')
    list_filter = ('event_type', 'status', 'is_featured')
    search_fields = ('title', 'description', 'location')
    list_editable = ('status', 'is_featured')


@admin.register(EventStat)
class EventStatAdmin(admin.ModelAdmin):
    list_display = ('events_hosted', 'participants', 'winners_crowned', 'collaborations')
