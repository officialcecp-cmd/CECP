import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'cecp_project.settings'
django.setup()

from django.test import Client

c = Client()

results = []

def test(num, label, response, expect):
    ok = response.status_code == expect
    status = "PASS" if ok else "FAIL"
    results.append((num, label, response.status_code, expect, ok))
    print(f"  [{status}] {num}. {label}: got {response.status_code}, expected {expect}")
    return ok

print("=" * 60)
print("CECP Backend Route Test Suite")
print("=" * 60)

# Public routes
test(1, "Landing page", c.get('/'), 200)
test(2, "Login page (GET)", c.get('/login/'), 200)

# Login flow
test(3, "Login (POST)", c.post('/login/', {'username': 'clubhead', 'password': 'cecp2025'}), 302)

# Authenticated routes (session preserved in client)
test(4, "Dashboard", c.get('/dashboard/'), 200)
test(5, "Submit Project (GET)", c.get('/submit-project/'), 200)
test(6, "Approvals page", c.get('/approvals/'), 200)

# Submit a test project
from landing.models import ProjectCategory
cat = ProjectCategory.objects.first()
r = c.post('/submit-project/', {
    'title': 'Test Backend Project',
    'description': 'Automated test submission',
    'spec': 'A simple Arduino LED blinker project for beginners',
    'status': 'active',
    'tech_stack_input': 'Arduino, LED, C++',
    'category': cat.id if cat else '',
})
test(7, "Submit Project (POST)", r, 302)

# Check the project was created and auto-approved (club head)
from landing.models import Project
proj = Project.objects.filter(title='Test Backend Project').first()
if proj:
    print(f"  [INFO] Project created: approval={proj.approval_status}, level={proj.level}")
else:
    print("  [FAIL] Project was NOT created!")

# Reject API test (need a pending project)
from landing.models import ClubMember
from django.contrib.auth.models import User
test_user, _ = User.objects.get_or_create(username='testmember', defaults={'first_name': 'Test', 'last_name': 'Member'})
test_user.set_password('test1234')
test_user.save()
test_member, _ = ClubMember.objects.get_or_create(user=test_user, defaults={'role': 'member', 'member_id': 'CECP-2025-099'})

# Create a pending project
pending = Project.objects.create(
    title='Pending Test', description='Test', spec='test', 
    status='active', approval_status='pending', submitted_by=test_member
)

# Approve it
test(8, "Approve API", c.post(f'/api/approve/{pending.id}/'), 200)

# Create another pending to test reject
pending2 = Project.objects.create(
    title='Reject Test', description='Test', spec='test',
    status='active', approval_status='pending', submitted_by=test_member
)
test(9, "Reject API", c.post(f'/api/reject/{pending2.id}/', {'reason': 'Not complete'}), 200)

# Check notifications were created
from landing.models import Notification
notifs = Notification.objects.filter(recipient=test_member)
print(f"  [INFO] Notifications for test member: {notifs.count()}")

# Mark notification read
if notifs.exists():
    # Login as test member
    c2 = Client()
    c2.login(username='testmember', password='test1234')
    test(10, "Mark notification read", c2.post(f'/api/notification/{notifs.first().id}/read/'), 200)

# Logout
test(11, "Logout", c.get('/logout/'), 302)

# Protected routes should redirect when logged out
test(12, "Dashboard (anon)", c.get('/dashboard/'), 302)
test(13, "Submit (anon)", c.get('/submit-project/'), 302)
test(14, "Approvals (anon)", c.get('/approvals/'), 302)

# Member cannot access approvals
c3 = Client()
c3.login(username='testmember', password='test1234')
r = c3.get('/approvals/')
test(15, "Approvals (member)", r, 302)

# Cleanup test data
Project.objects.filter(title__in=['Test Backend Project', 'Pending Test', 'Reject Test']).delete()
Notification.objects.filter(recipient=test_member).delete()

print()
passed = sum(1 for r in results if r[4])
total = len(results)
print(f"Results: {passed}/{total} tests passed")
if passed == total:
    print("ALL TESTS PASSED - Backend is error-free!")
else:
    print("SOME TESTS FAILED - see above for details")
