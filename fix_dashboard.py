with open('landing/views.py', 'rb') as f:
    content = f.read()

old = b"""@user_passes_test(is_admin, login_url='/login/')\r\ndef moderator_dashboard(request):\r\n    pending_blogs = Blog.objects.filter(is_approved=False).order_by('-created_at')\r\n    pending_apps = ClubApplication.objects.filter(status='pending').order_by('-created_at')\r\n    return render(request, 'landing/moderator_dashboard.html', {\r\n        'pending_blogs': pending_blogs,\r\n        'pending_apps': pending_apps,\r\n        'page_title': 'Moderator Dashboard - CECP'\r\n    })"""

new = b"""@user_passes_test(is_admin, login_url='/login/')\r\ndef moderator_dashboard(request):\r\n    pending_blogs = Blog.objects.filter(is_approved=False).order_by('-created_at')\r\n    pending_apps = ClubApplication.objects.filter(status='pending').order_by('-created_at')\r\n    pending_projects = Project.objects.filter(\r\n        approval_status='pending'\r\n    ).select_related('submitted_by', 'category').order_by('-created_at')\r\n    return render(request, 'landing/moderator_dashboard.html', {\r\n        'pending_blogs': pending_blogs,\r\n        'pending_apps': pending_apps,\r\n        'pending_projects': pending_projects,\r\n        'page_title': 'Moderator Dashboard - CECP'\r\n    })"""

if old in content:
    content = content.replace(old, new)
    with open('landing/views.py', 'wb') as f:
        f.write(content)
    print("SUCCESS: moderator_dashboard patched!")
else:
    print("FAILED: could not find target block.")
    # Print bytes around line 702 to debug
    lines = content.split(b'\n')
    for i in range(700, 712):
        print(repr(lines[i]))
