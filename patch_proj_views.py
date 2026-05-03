import re

with open('landing/views.py', 'rb') as f:
    content = f.read()

# Replace moderator_dashboard
old_mod_dash = b"""def moderator_dashboard(request):
    pending_blogs = Blog.objects.filter(is_approved=False).order_by('-created_at')
    pending_apps = ClubApplication.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'landing/moderator_dashboard.html', {
        'pending_blogs': pending_blogs,
        'pending_apps': pending_apps,
        'page_title': 'Moderator Dashboard - CECP'
    })"""

new_mod_dash = b"""def moderator_dashboard(request):
    pending_blogs = Blog.objects.filter(is_approved=False).order_by('-created_at')
    pending_apps = ClubApplication.objects.filter(status='pending').order_by('-created_at')
    pending_projects = Project.objects.filter(is_approved=False).order_by('-created_at')
    return render(request, 'landing/moderator_dashboard.html', {
        'pending_blogs': pending_blogs,
        'pending_apps': pending_apps,
        'pending_projects': pending_projects,
        'page_title': 'Moderator Dashboard - CECP'
    })"""

content = content.replace(old_mod_dash, new_mod_dash)

new_project_views = b"""

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def approve_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.is_approved = True
    project.save()
    messages.success(request, f'Project "{project.title}" has been approved and published.')
    return redirect('landing:moderator_dashboard')

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def reject_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    messages.success(request, f'Project "{project.title}" has been rejected and deleted.')
    return redirect('landing:moderator_dashboard')
"""

if b'def approve_project' not in content:
    content += new_project_views

with open('landing/views.py', 'wb') as f:
    f.write(content)

print("Patched views.py for projects!")
