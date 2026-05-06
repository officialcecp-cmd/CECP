# ==============================================================================
# Landing App — URL Configuration
# ==============================================================================
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'landing'

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('team/', views.team_view, name='team'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),

    # Authentication
    path('login/', views.auth_portal, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.member_logout, name='logout'),

    # Password Reset (Django built-in views with custom templates)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='landing/password_reset.html',
             email_template_name='landing/emails/password_reset_email.html',
             subject_template_name='landing/emails/password_reset_subject.txt',
             success_url='/password-reset/sent/',
         ),
         name='password_reset'),
    path('password-reset/sent/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='landing/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='landing/password_reset_confirm.html',
             success_url='/password-reset/complete/',
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='landing/password_reset_complete.html',
         ),
         name='password_reset_complete'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('member/dashboard/', views.member_dashboard, name='member_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Project Management
    path('submit-project/', views.submit_project, name='submit_project'),
    path('submit-blog/', views.submit_blog, name='submit_blog'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('moderator-dashboard/', views.moderator_dashboard, name='moderator_dashboard'),
    path('approve-blog/<int:blog_id>/', views.approve_blog, name='approve_blog'),
    path('reject-blog/<int:blog_id>/', views.reject_blog, name='reject_blog'),
    path('edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('accept-application/<int:app_id>/', views.accept_application, name='accept_application'),
    path('reject-application/<int:app_id>/', views.reject_application, name='reject_application'),
    path('review-application/<int:application_id>/', views.review_application, name='review_application'),
    path('approve-project/<int:project_id>/', views.approve_project, name='approve_project'),
    path('reject-project/<int:project_id>/', views.reject_project, name='reject_project'),
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
    path('download-resume/<int:application_id>/', views.download_resume, name='download_resume'),
]
