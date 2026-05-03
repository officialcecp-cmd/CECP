import re

with open('landing/urls.py', 'rb') as f:
    content = f.read()

new_urls = b"""    path('accept-application/<int:app_id>/', views.accept_application, name='accept_application'),
    path('reject-application/<int:app_id>/', views.reject_application, name='reject_application'),
    path('approve-project/<int:project_id>/', views.approve_project, name='approve_project'),
    path('reject-project/<int:project_id>/', views.reject_project, name='reject_project'),"""

old_urls = b"""    path('accept-application/<int:app_id>/', views.accept_application, name='accept_application'),
    path('reject-application/<int:app_id>/', views.reject_application, name='reject_application'),"""

content = content.replace(old_urls, new_urls)
with open('landing/urls.py', 'wb') as f:
    f.write(content)
print('urls.py patched for projects')
