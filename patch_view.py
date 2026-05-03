import re

with open('landing/views.py', 'rb') as f:
    content = f.read()

new_views = b'''
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='CECP_Admins').exists())

@user_passes_test(is_admin, login_url='/login/')
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
    return redirect('landing:moderator_dashboard')
'''

if b'def moderator_dashboard(' not in content:
    content += new_views
    with open('landing/views.py', 'wb') as f:
        f.write(content)
    print("Patched views.py with moderator_dashboard")
else:
    print("Already patched views.py")
