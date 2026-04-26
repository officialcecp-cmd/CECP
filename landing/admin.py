# ==============================================================================
# Landing App — Admin Configuration
# ==============================================================================
from django.contrib import admin
from .models import (
    Initiative, Project, TeamMember,
    ClubMember, ProjectCategory, Notification, ClubApplication
)
from .services import categorize_project_level


# --- Club Member Admin --------------------------------------------------------

@admin.register(ClubMember)
class ClubMemberAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'member_id', 'role', 'is_active', 'joined_at')
    list_editable = ('role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'member_id')
    raw_id_fields = ('user',)


# --- Project Category Admin ---------------------------------------------------

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'display_order')
    list_editable = ('display_order',)
    prepopulated_fields = {'slug': ('name',)}


# --- Project Admin (with AI auto-categorization) ------------------------------

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'category', 'approval_status', 'status', 'submitted_by', 'is_featured')
    list_editable = ('approval_status', 'is_featured')
    list_filter = ('approval_status', 'status', 'level', 'category', 'is_featured')
    search_fields = ('title', 'codename', 'description', 'spec')
    readonly_fields = ('level', 'created_at', 'updated_at')
    raw_id_fields = ('submitted_by', 'approved_by')
    filter_horizontal = ('team_members',)
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
            'fields': ('github_url', 'demo_url', 'documentation_url'),
            'classes': ('collapse',)
        }),
        ('Team & Display', {
            'fields': ('team_members', 'status', 'is_featured', 'display_order')
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

        # ✅ Auto-approve when a superuser or staff adds a project via admin
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


# --- Team Member Admin --------------------------------------------------------

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'title', 'is_active', 'display_order')
    list_editable = ('role', 'is_active', 'display_order')
    list_filter = ('role', 'is_active')
    search_fields = ('name', 'title')


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
    readonly_fields = ('created_at', 'updated_at', 'reviewed_by')
    actions = ['approve_applications', 'reject_applications']

    fieldsets = (
        ('Applicant Identity', {
            'fields': ('full_name', 'email', 'whatsapp_number', 'roll_number')
        }),
        ('Academic Info', {
            'fields': ('branch', 'current_year', 'domain_of_interest')
        }),
        ('Skills & Motivation', {
            'fields': ('skill_level', 'motivation', 'github_url', 'linkedin_url')
        }),
        ('Review', {
            'fields': ('status', 'reviewed_by', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Auto-capture the logged-in admin if status is changed to Approved/Rejected
        if obj.status in ['approved', 'rejected']:
            if hasattr(request.user, 'club_profile'):
                obj.reviewed_by = request.user.club_profile
        elif obj.status == 'pending':
            # Reset if changed back to pending
            obj.reviewed_by = None
            
        super().save_model(request, obj, form, change)

    @admin.action(description='\u2705 Approve selected applications')
    def approve_applications(self, request, queryset):
        reviewer = getattr(request.user, 'club_profile', None)
        if reviewer:
            updated = queryset.update(status='approved', reviewed_by=reviewer)
        else:
            updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} application(s) approved.')

    @admin.action(description='\u274c Reject selected applications')
    def reject_applications(self, request, queryset):
        reviewer = getattr(request.user, 'club_profile', None)
        if reviewer:
            updated = queryset.update(status='rejected', reviewed_by=reviewer)
        else:
            updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} application(s) rejected.')
