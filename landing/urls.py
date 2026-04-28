# ==============================================================================
# Landing App — URL Configuration
# ==============================================================================
from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),

    # Authentication
    path('login/', views.auth_portal, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.member_logout, name='logout'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('member/dashboard/', views.member_dashboard, name='member_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Project Management
    path('submit-project/', views.submit_project, name='submit_project'),
    path('api/delete-project/<int:project_id>/', views.delete_project, name='delete_project'),

    # Approvals
    path('approvals/', views.approval_dashboard, name='approvals'),
    path('api/approve/<int:project_id>/', views.approve_project, name='approve_project'),
    path('api/reject/<int:project_id>/', views.reject_project, name='reject_project'),

    # Notifications
    path('api/notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # Club Application
    path('apply/', views.apply_view, name='apply'),
    path('apply/success/', views.apply_success_view, name='apply_success'),
    path('apply/delete/', views.delete_application, name='delete_application'),
]
