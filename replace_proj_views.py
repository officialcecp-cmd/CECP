with open('landing/views.py', 'rb') as f:
    content = f.read()

old_approve = b"""@login_required(login_url='/login/')\r\n@require_POST\r\ndef approve_project(request, project_id):\r\n    try:\r\n        member = request.user.club_profile\r\n    except ClubMember.DoesNotExist:\r\n        return JsonResponse({'error': 'No club profile'}, status=403)\r\n    if not member.can_approve_projects:\r\n        return JsonResponse({'error': 'Permission denied'}, status=403)\r\n\r\n    project = get_object_or_404(Project, id=project_id, approval_status='pending')\r\n    project.approval_status = 'approved'\r\n    project.approved_by = member\r\n    project.save()\r\n\r\n    if project.submitted_by:\r\n        Notification.objects.create(\r\n            recipient=project.submitted_by, notification_type='approved',\r\n            title=f'Project Approved: {project.title}',\r\n            message=f'Your project \"{project.title}\" has been approved by {member.display_name}!',\r\n            related_project=project,\r\n        )\r\n    return JsonResponse({'status': 'approved', 'project_id': project_id})"""

new_approve = b"""@user_passes_test(is_admin, login_url='/login/')\r\n@require_POST\r\ndef approve_project(request, project_id):\r\n    project = get_object_or_404(Project, id=project_id)\r\n    project.approval_status = 'approved'\r\n    project.is_approved = True\r\n    project.save()\r\n\r\n    # Send notification to submitter\r\n    try:\r\n        if project.submitted_by:\r\n            Notification.objects.create(\r\n                recipient=project.submitted_by, notification_type='approved',\r\n                title=f'Project Approved: {project.title}',\r\n                message=f'Your project \"{project.title}\" has been approved and is now live!',\r\n                related_project=project,\r\n            )\r\n    except Exception:\r\n        pass\r\n\r\n    messages.success(request, f'Project \"{project.title}\" has been approved and published.')\r\n    return redirect('landing:moderator_dashboard')"""

old_reject = b"""@login_required(login_url='/login/')\r\n@require_POST\r\ndef reject_project(request, project_id):\r\n    try:\r\n        member = request.user.club_profile\r\n    except ClubMember.DoesNotExist:\r\n        return JsonResponse({'error': 'No club profile'}, status=403)\r\n    if not member.can_approve_projects:\r\n        return JsonResponse({'error': 'Permission denied'}, status=403)\r\n\r\n    project = get_object_or_404(Project, id=project_id, approval_status='pending')\r\n    reason = request.POST.get('reason', 'No reason provided')\r\n    project.approval_status = 'rejected'\r\n    project.rejection_reason = reason\r\n    project.approved_by = member\r\n    project.save()\r\n\r\n    if project.submitted_by:\r\n        Notification.objects.create(\r\n            recipient=project.submitted_by, notification_type='rejected',\r\n            title=f'Project Rejected: {project.title}',\r\n            message=f'Your project \"{project.title}\" was not approved. Reason: {reason}',\r\n            related_project=project,\r\n        )\r\n    return JsonResponse({'status': 'rejected', 'project_id': project_id})"""

new_reject = b"""@user_passes_test(is_admin, login_url='/login/')\r\n@require_POST\r\ndef reject_project(request, project_id):\r\n    project = get_object_or_404(Project, id=project_id)\r\n    title = project.title\r\n    project.delete()\r\n    messages.success(request, f'Project \"{title}\" has been rejected and removed.')\r\n    return redirect('landing:moderator_dashboard')"""

changed = False
if old_approve in content:
    content = content.replace(old_approve, new_approve)
    print("approve_project: replaced OK")
    changed = True
else:
    print("approve_project: target block NOT FOUND")

if old_reject in content:
    content = content.replace(old_reject, new_reject)
    print("reject_project: replaced OK")
    changed = True
else:
    print("reject_project: target block NOT FOUND")

if changed:
    with open('landing/views.py', 'wb') as f:
        f.write(content)
    print("views.py saved!")
