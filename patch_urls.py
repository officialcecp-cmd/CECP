import re

with open('landing/urls.py', 'rb') as f:
    content = f.read()

old_url = b"path('approve-blog/<int:blog_id>/', views.approve_blog, name='approve_blog'),"
new_urls = b"""path('approve-blog/<int:blog_id>/', views.approve_blog, name='approve_blog'),
    path('reject-blog/<int:blog_id>/', views.reject_blog, name='reject_blog'),
    path('edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('accept-application/<int:app_id>/', views.accept_application, name='accept_application'),
    path('reject-application/<int:app_id>/', views.reject_application, name='reject_application'),"""

if old_url in content:
    content = content.replace(old_url, new_urls)
    with open('landing/urls.py', 'wb') as f:
        f.write(content)
    print('urls.py patched')
else:
    print('Could not find old_url in urls.py')
