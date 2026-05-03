with open('landing/views.py', 'rb') as f:
    content = f.read()

old = b"def project_detail(request, project_id):\r\n    project = get_object_or_404(Project, id=project_id, approval_status='approved')"
new = b"""def project_detail(request, project_id):\r\n    # Allow admins to preview pending projects; public only sees approved ones\r\n    if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='CECP_Admins').exists()):\r\n        project = get_object_or_404(Project, id=project_id)\r\n    else:\r\n        project = get_object_or_404(Project, id=project_id, approval_status='approved')"""

if old in content:
    content = content.replace(old, new)
    with open('landing/views.py', 'wb') as f:
        f.write(content)
    print("project_detail patched OK!")
else:
    print("Could not find target block.")
