with open('landing/views.py', 'rb') as f:
    content = f.read()

# Check if approve_project already exists
if b'def approve_project' in content:
    print("approve_project already exists - will update instead")
else:
    print("approve_project missing - appending")
    new_views = b"""
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def approve_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.approval_status = 'approved'
    project.is_approved = True
    project.save()
    messages.success(request, f'Project "{project.title}" has been approved and published.')
    return redirect('landing:moderator_dashboard')

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def reject_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    title = project.title
    project.delete()
    messages.success(request, f'Project "{title}" has been rejected and deleted.')
    return redirect('landing:moderator_dashboard')
"""
    content = content + new_views
    with open('landing/views.py', 'wb') as f:
        f.write(content)
    print("SUCCESS: approve_project and reject_project appended!")
