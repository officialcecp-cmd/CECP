import re

with open('landing/views.py', 'rb') as f:
    content = f.read()

# First, ensure ClubApplication and Blog are imported if not already. They should be at the top.
# Then find moderator_dashboard

# We will replace the existing moderator views with the new ones.
old_views = b'''@user_passes_test(is_admin, login_url='/login/')
def moderator_dashboard(request):
    pending_blogs = Blog.objects.filter(is_approved=False).order_by('-created_at')
    return render(request, 'landing/moderator_dashboard.html', {
        'pending_blogs': pending_blogs,
        'page_title': 'Moderator Dashboard - CECP'
    })

@user_passes_test(is_admin, login_url='/login/')
@require_POST
def approve_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    blog.is_approved = True
    blog.save()
    messages.success(request, f'Blog "{blog.title}" has been approved and published.')
    return redirect('landing:moderator_dashboard')'''

new_views = b'''@user_passes_test(is_admin, login_url='/login/')
def moderator_dashboard(request):
    pending_blogs = Blog.objects.filter(is_approved=False).order_by('-created_at')
    pending_apps = ClubApplication.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'landing/moderator_dashboard.html', {
        'pending_blogs': pending_blogs,
        'pending_apps': pending_apps,
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
    return redirect('landing:moderator_dashboard')'''

if old_views in content:
    content = content.replace(old_views, new_views)
    with open('landing/views.py', 'wb') as f:
        f.write(content)
    print("Patched views.py successfully!")
else:
    print("Could not find the old views block. Trying regex replacement...")
    # More robust replacement if line endings differ
    import re
    old_pattern = re.compile(b'@user_passes_test\\(is_admin, login_url=\'/login/\'\\)\\s*\n*def moderator_dashboard\\(request\\):.*?(?=@user_passes_test|\\Z)', re.DOTALL)
    # wait, this could be tricky. Let's just append if not found, but we want to avoid duplicates.
    # Let's hope the direct replace works (it should since we just wrote it).
