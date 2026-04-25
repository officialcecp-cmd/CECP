# ==============================================================================
# Landing App — Admin Configuration
# ==============================================================================
from django.contrib import admin
from .models import (
    Initiative, Project, TeamMember,
    ClubMember, ProjectCategory, Notification
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
