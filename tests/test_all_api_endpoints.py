"""
Automated Test Suite checking every single API endpoint in TaskFlow against the running local server.
"""
import sys
import time
import requests

# Reconfigure stdout for safe Windows output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"

def log_test(name, success, detail=""):
    badge = "[PASS]" if success else "[FAIL]"
    print(f"{badge} | {name} {f'- {detail}' if detail else ''}")
    assert success, f"Test failed: {name} - {detail}"

def test_all_endpoints():
    print("\n" + "="*60)
    print(">>> EXHAUSTIVE API ENDPOINTS VERIFICATION SUITE")
    print("="*60)

    # 1. Health Check
    res = requests.get(f"{BASE_URL}/health")
    log_test("GET /health", res.status_code == 200 and res.json().get("status") == "ok", f"Status: {res.status_code}")

    # 2. Auth: Login with seeded manager
    login_payload = {"email": "manager@acme.com", "password": "Test@Password123"}
    res = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_payload)
    log_test("POST /api/v1/auth/login (manager)", res.status_code == 200 and "access_token" in res.json(), f"Status: {res.status_code}")
    tokens = res.json()
    mgr_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    # 3. Auth: Login with seeded employee
    res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "bob@acme.com", "password": "Test@Password123"})
    log_test("POST /api/v1/auth/login (employee)", res.status_code == 200 and "access_token" in res.json(), f"Status: {res.status_code}")
    emp_token = res.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # 4. Auth: Refresh token
    res = requests.post(f"{BASE_URL}/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    log_test("POST /api/v1/auth/refresh", res.status_code == 200 and "access_token" in res.json(), f"Status: {res.status_code}")

    # 5. Auth: Signup a new test user
    ts = int(time.time())
    new_user_payload = {
        "email": f"tester_{ts}@acme.com",
        "password": "Test@Password123",
        "full_name": "API Test User",
        "organization_name": "Acme Corp",
        "role": "member"
    }
    res = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=new_user_payload)
    log_test("POST /api/v1/auth/signup", res.status_code == 201 and res.json().get("email") == new_user_payload["email"], f"Created ID: {res.json().get('id')}")
    new_user_id = res.json()["id"]

    # 6. Auth: GET /me
    res = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=mgr_headers)
    log_test("GET /api/v1/auth/me", res.status_code == 200 and res.json().get("email") == "manager@acme.com", f"User: {res.json().get('full_name')}")

    # 7. Auth: PATCH /me
    res = requests.patch(f"{BASE_URL}/api/v1/auth/me", json={"full_name": "Alice Vance (Manager)"}, headers=mgr_headers)
    log_test("PATCH /api/v1/auth/me", res.status_code == 200 and res.json().get("full_name") == "Alice Vance (Manager)", f"Status: {res.status_code}")

    # 8. Users: Search users
    res = requests.get(f"{BASE_URL}/api/v1/users/search?q=bob", headers=mgr_headers)
    log_test("GET /api/v1/users/search", res.status_code == 200 and len(res.json()) >= 1, f"Found {len(res.json())} users")

    # 9. Users: Organization users
    res = requests.get(f"{BASE_URL}/api/v1/users/organization", headers=mgr_headers)
    log_test("GET /api/v1/users/organization", res.status_code == 200 and len(res.json()) >= 4, f"Organization members: {len(res.json())}")

    # 10. Dashboard: Summary metrics
    res = requests.get(f"{BASE_URL}/api/v1/dashboard", headers=mgr_headers)
    dash_data = res.json()
    log_test("GET /api/v1/dashboard (manager)", res.status_code == 200 and "total_projects" in dash_data and "total_tasks" in dash_data,
             f"Projects: {dash_data.get('total_projects')}, Tasks: {dash_data.get('total_tasks')}")

    res = requests.get(f"{BASE_URL}/api/v1/dashboard", headers=emp_headers)
    log_test("GET /api/v1/dashboard (employee)", res.status_code == 200 and "my_assigned_tasks" in res.json(),
             f"Assigned tasks: {len(res.json().get('my_assigned_tasks', []))}")

    # 11. Projects: List projects
    res = requests.get(f"{BASE_URL}/api/v1/projects", headers=mgr_headers)
    projects = res.json()
    log_test("GET /api/v1/projects", res.status_code == 200 and len(projects) >= 3, f"Total projects: {len(projects)}")

    # 12. Projects: Create project
    proj_payload = {
        "name": f"Test Automation Project {ts}",
        "description": "Created during automated verification",
        "member_ids": []
    }
    res = requests.post(f"{BASE_URL}/api/v1/projects", json=proj_payload, headers=mgr_headers)
    log_test("POST /api/v1/projects", res.status_code == 201 and "id" in res.json(), f"Project ID: {res.json().get('id')}")
    test_proj_id = res.json()["id"]

    # 13. Projects: Get project detail
    res = requests.get(f"{BASE_URL}/api/v1/projects/{test_proj_id}", headers=mgr_headers)
    log_test("GET /api/v1/projects/{project_id}", res.status_code == 200 and res.json().get("name") == proj_payload["name"], f"Name: {res.json().get('name')}")

    # 14. Projects: Update project
    res = requests.patch(f"{BASE_URL}/api/v1/projects/{test_proj_id}", json={"description": "Updated project description"}, headers=mgr_headers)
    log_test("PATCH /api/v1/projects/{project_id}", res.status_code == 200 and res.json().get("description") == "Updated project description", f"Status: {res.status_code}")

    # 15. Members: Add member to project
    res = requests.post(f"{BASE_URL}/api/v1/projects/{test_proj_id}/members", json={"user_id": new_user_id, "role": "member"}, headers=mgr_headers)
    log_test("POST /api/v1/projects/{project_id}/members", res.status_code == 201, f"Added user {new_user_id}")

    # 16. Members: List members
    res = requests.get(f"{BASE_URL}/api/v1/projects/{test_proj_id}/members", headers=mgr_headers)
    log_test("GET /api/v1/projects/{project_id}/members", res.status_code == 200 and len(res.json()) >= 2, f"Member count: {len(res.json())}")

    # 17. Members: Update member role
    res = requests.patch(f"{BASE_URL}/api/v1/projects/{test_proj_id}/members/{new_user_id}", json={"role": "manager"}, headers=mgr_headers)
    log_test("PATCH /api/v1/projects/{project_id}/members/{user_id}", res.status_code == 200 and res.json().get("role") == "manager", f"Role: {res.json().get('role')}")

    # 18. Tasks: Create task
    task_payload = {
        "title": f"Test Task {ts}",
        "description": "Automated verification task",
        "priority": "high",
        "status": "todo",
        "assignee_id": new_user_id
    }
    res = requests.post(f"{BASE_URL}/api/v1/projects/{test_proj_id}/tasks", json=task_payload, headers=mgr_headers)
    log_test("POST /api/v1/projects/{project_id}/tasks", res.status_code == 201 and "id" in res.json(), f"Task ID: {res.json().get('id')}")
    test_task_id = res.json()["id"]

    # 19. Tasks: List tasks
    res = requests.get(f"{BASE_URL}/api/v1/projects/{test_proj_id}/tasks", headers=mgr_headers)
    log_test("GET /api/v1/projects/{project_id}/tasks", res.status_code == 200 and len(res.json()) >= 1, f"Tasks count: {len(res.json())}")

    # 20. Tasks: Get specific task
    res = requests.get(f"{BASE_URL}/api/v1/projects/{test_proj_id}/tasks/{test_task_id}", headers=mgr_headers)
    log_test("GET /api/v1/projects/{project_id}/tasks/{task_id}", res.status_code == 200 and res.json().get("title") == task_payload["title"], f"Title: {res.json().get('title')}")

    # 21. Tasks: Patch task
    res = requests.patch(f"{BASE_URL}/api/v1/projects/{test_proj_id}/tasks/{test_task_id}", json={"status": "in_progress", "priority": "critical"}, headers=mgr_headers)
    log_test("PATCH /api/v1/projects/{project_id}/tasks/{task_id}", res.status_code == 200 and res.json().get("status") == "in_progress", f"Status: {res.json().get('status')}")

    # 22. Tasks: Delete task
    res = requests.delete(f"{BASE_URL}/api/v1/projects/{test_proj_id}/tasks/{test_task_id}", headers=mgr_headers)
    log_test("DELETE /api/v1/projects/{project_id}/tasks/{task_id}", res.status_code == 204, f"Deleted Task {test_task_id}")

    # 23. Members: Remove member
    res = requests.delete(f"{BASE_URL}/api/v1/projects/{test_proj_id}/members/{new_user_id}", headers=mgr_headers)
    log_test("DELETE /api/v1/projects/{project_id}/members/{user_id}", res.status_code == 204, f"Removed Member {new_user_id}")

    # 24. Projects: Delete (archive) project
    res = requests.delete(f"{BASE_URL}/api/v1/projects/{test_proj_id}", headers=mgr_headers)
    log_test("DELETE /api/v1/projects/{project_id}", res.status_code == 204, f"Archived Project {test_proj_id}")

    print("\n" + "="*60)
    print("SUCCESS: ALL API ENDPOINTS TESTED AND VERIFIED SUCCESSFULLY!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_all_endpoints()
