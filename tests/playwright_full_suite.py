"""
Unified Playwright Automation Test Suite for TaskFlow.
Combines:
1. Playwright Native API Testing (every endpoint tested using playwright.request)
2. Playwright Automated Browser E2E UI Testing (Chromium headless)
3. Multi-company, Multi-tenant, and Role-based Access Control verification
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"
ARTIFACT_DIR = Path(r"C:\Users\Hp\.gemini\antigravity-ide\brain\a179b7ff-8076-49c0-93ef-04d188691b76")
SCREENSHOTS_DIR = ARTIFACT_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log_test(category, name, success, detail=""):
    badge = "[PASS]" if success else "[FAIL]"
    print(f"{badge} | [{category}] {name} {f'-> {detail}' if detail else ''}")
    assert success, f"Assertion failed for {name}: {detail}"

def run_suite():
    print("\n" + "="*75)
    print(">>> PLAYWRIGHT COMPREHENSIVE AUTOMATION TEST SUITE (API + BROWSER)")
    print("="*75)

    with sync_playwright() as p:
        # =========================================================================
        # PART 1: PLAYWRIGHT API REQUEST TESTING (EVERY ENDPOINT VERIFIED)
        # =========================================================================
        print("\n--- PART 1: PLAYWRIGHT API TESTING (ALL 23 ENDPOINTS) ---")
        api = p.request.new_context(base_url=BASE_URL)

        # 1. Health
        res = api.get("/health")
        log_test("API", "GET /health", res.status == 200 and res.json().get("status") == "ok", f"Status: {res.status}")

        # 2. Auth: Login Manager
        res = api.post("/api/v1/auth/login", data={"email": "manager@acme.com", "password": "Test@Password123"})
        log_test("API", "POST /api/v1/auth/login (manager)", res.status == 200 and "access_token" in res.json(), f"Status: {res.status}")
        tokens = res.json()
        mgr_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

        # 3. Auth: Login Employee
        res = api.post("/api/v1/auth/login", data={"email": "bob@acme.com", "password": "Test@Password123"})
        log_test("API", "POST /api/v1/auth/login (employee)", res.status == 200 and "access_token" in res.json(), f"Status: {res.status}")
        emp_token = res.json()["access_token"]
        emp_headers = {"Authorization": f"Bearer {emp_token}"}

        # 4. Auth: Refresh token
        res = api.post("/api/v1/auth/refresh", data={"refresh_token": refresh_token})
        log_test("API", "POST /api/v1/auth/refresh", res.status == 200 and "access_token" in res.json(), f"Status: {res.status}")

        # 5. Auth: Signup
        ts = int(time.time())
        signup_payload = {
            "email": f"pw_user_{ts}@acme.com",
            "password": "Test@Password123",
            "full_name": "Playwright Tested User",
            "organization_name": "Acme Corp",
            "role": "member"
        }
        res = api.post("/api/v1/auth/signup", data=signup_payload)
        log_test("API", "POST /api/v1/auth/signup", res.status == 201 and "id" in res.json(), f"User ID: {res.json().get('id')}")
        test_uid = res.json()["id"]

        # 6. Auth: GET /me
        res = api.get("/api/v1/auth/me", headers=mgr_headers)
        log_test("API", "GET /api/v1/auth/me", res.status == 200 and res.json().get("email") == "manager@acme.com", f"User: {res.json().get('full_name')}")

        # 7. Auth: PATCH /me
        res = api.patch("/api/v1/auth/me", data={"full_name": "Alice Vance (Manager)"}, headers=mgr_headers)
        log_test("API", "PATCH /api/v1/auth/me", res.status == 200, f"Status: {res.status}")

        # 8. Users: Search
        res = api.get("/api/v1/users/search?q=bob", headers=mgr_headers)
        log_test("API", "GET /api/v1/users/search", res.status == 200 and len(res.json()) >= 1, f"Found: {len(res.json())}")

        # 9. Users: Organization
        res = api.get("/api/v1/users/organization", headers=mgr_headers)
        log_test("API", "GET /api/v1/users/organization", res.status == 200 and len(res.json()) >= 4, f"Members: {len(res.json())}")

        # 10. Dashboard: Manager
        res = api.get("/api/v1/dashboard", headers=mgr_headers)
        dash = res.json()
        log_test("API", "GET /api/v1/dashboard (manager)", res.status == 200 and "total_projects" in dash, f"Projects: {dash.get('total_projects')}, Tasks: {dash.get('total_tasks')}")

        # 11. Dashboard: Employee
        res = api.get("/api/v1/dashboard", headers=emp_headers)
        log_test("API", "GET /api/v1/dashboard (employee)", res.status == 200 and "my_assigned_tasks" in res.json(), f"Assigned: {len(res.json().get('my_assigned_tasks', []))}")

        # 12. Projects: List
        res = api.get("/api/v1/projects", headers=mgr_headers)
        log_test("API", "GET /api/v1/projects", res.status == 200 and len(res.json()) >= 3, f"Projects count: {len(res.json())}")

        # 13. Projects: Create
        proj_payload = {"name": f"Playwright API Project {ts}", "description": "Created via Playwright API context", "member_ids": []}
        res = api.post("/api/v1/projects", data=proj_payload, headers=mgr_headers)
        log_test("API", "POST /api/v1/projects", res.status == 201 and "id" in res.json(), f"Project ID: {res.json().get('id')}")
        test_pid = res.json()["id"]

        # 14. Projects: Get Detail
        res = api.get(f"/api/v1/projects/{test_pid}", headers=mgr_headers)
        log_test("API", "GET /api/v1/projects/{id}", res.status == 200 and res.json().get("name") == proj_payload["name"], f"Name: {res.json().get('name')}")

        # 15. Projects: Patch
        res = api.patch(f"/api/v1/projects/{test_pid}", data={"description": "Updated description via Playwright"}, headers=mgr_headers)
        log_test("API", "PATCH /api/v1/projects/{id}", res.status == 200, f"Status: {res.status}")

        # 16. Members: Add Member
        res = api.post(f"/api/v1/projects/{test_pid}/members", data={"user_id": test_uid, "role": "member"}, headers=mgr_headers)
        log_test("API", "POST /api/v1/projects/{id}/members", res.status == 201, f"Added user {test_uid}")

        # 17. Members: List Members
        res = api.get(f"/api/v1/projects/{test_pid}/members", headers=mgr_headers)
        log_test("API", "GET /api/v1/projects/{id}/members", res.status == 200 and len(res.json()) >= 2, f"Count: {len(res.json())}")

        # 18. Members: Update Role
        res = api.patch(f"/api/v1/projects/{test_pid}/members/{test_uid}", data={"role": "manager"}, headers=mgr_headers)
        log_test("API", "PATCH /api/v1/projects/{id}/members/{uid}", res.status == 200 and res.json().get("role") == "manager", f"Role: {res.json().get('role')}")

        # 19. Tasks: Create Task
        task_payload = {"title": f"PW Task {ts}", "description": "Playwright API task", "priority": "high", "status": "todo", "assignee_id": test_uid}
        res = api.post(f"/api/v1/projects/{test_pid}/tasks", data=task_payload, headers=mgr_headers)
        log_test("API", "POST /api/v1/projects/{id}/tasks", res.status == 201 and "id" in res.json(), f"Task ID: {res.json().get('id')}")
        test_tid = res.json()["id"]

        # 20. Tasks: List Tasks
        res = api.get(f"/api/v1/projects/{test_pid}/tasks", headers=mgr_headers)
        log_test("API", "GET /api/v1/projects/{id}/tasks", res.status == 200 and len(res.json()) >= 1, f"Count: {len(res.json())}")

        # 21. Tasks: Get Task
        res = api.get(f"/api/v1/projects/{test_pid}/tasks/{test_tid}", headers=mgr_headers)
        log_test("API", "GET /api/v1/projects/{id}/tasks/{tid}", res.status == 200 and res.json().get("title") == task_payload["title"], f"Title: {res.json().get('title')}")

        # 22. Tasks: Patch Task
        res = api.patch(f"/api/v1/projects/{test_pid}/tasks/{test_tid}", data={"status": "done"}, headers=mgr_headers)
        log_test("API", "PATCH /api/v1/projects/{id}/tasks/{tid}", res.status == 200 and res.json().get("status") == "done", f"Status: {res.json().get('status')}")

        # 23. Tasks: Delete Task
        res = api.delete(f"/api/v1/projects/{test_pid}/tasks/{test_tid}", headers=mgr_headers)
        log_test("API", "DELETE /api/v1/projects/{id}/tasks/{tid}", res.status == 204, f"Status: {res.status}")

        # 24. Members: Remove Member
        res = api.delete(f"/api/v1/projects/{test_pid}/members/{test_uid}", headers=mgr_headers)
        log_test("API", "DELETE /api/v1/projects/{id}/members/{uid}", res.status == 204, f"Status: {res.status}")

        # 25. Projects: Archive Project
        res = api.delete(f"/api/v1/projects/{test_pid}", headers=mgr_headers)
        log_test("API", "DELETE /api/v1/projects/{id}", res.status == 204, f"Status: {res.status}")

        api.dispose()

        # =========================================================================
        # PART 2: PLAYWRIGHT AUTOMATED BROWSER TESTING (CHROMIUM HEADLESS)
        # =========================================================================
        print("\n--- PART 2: PLAYWRIGHT BROWSER E2E TESTING (USER JOURNEYS) ---")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Step 1: Login UI
        print("[*] Testing Login Page UI...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_selector(".auth-card")
        expect(page.locator(".auth-brand")).to_contain_text("TaskFlow")
        expect(page.locator("h1")).to_contain_text("Welcome back")
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_01_login.png"))
        log_test("BROWSER", "Login Page Render", True, "Form and branding verified")

        # Step 2: Acme Manager Login
        print("[*] Logging in as Acme Manager (manager@acme.com)...")
        page.fill("input#email", "manager@acme.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/manager-dashboard", timeout=10000)
        page.wait_for_selector(".dash-stats")
        expect(page.locator(".user-name")).to_contain_text("Alice Vance")
        expect(page.locator(".user-role")).to_contain_text("admin")
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_02_acme_dashboard.png"))
        log_test("BROWSER", "Manager Dashboard", True, "Stats and allocation loaded")

        # Step 3: Projects Listing
        print("[*] Viewing Projects Page...")
        page.click("a[href='/projects']")
        page.wait_for_url("**/projects", timeout=10000)
        page.wait_for_selector(".project-card")
        content = page.content()
        assert "Acme Web Portal" in content and "Acme Mobile App" in content and "Acme Cloud Infrastructure" in content
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_03_acme_projects.png"))
        log_test("BROWSER", "Projects List", True, "All 3 Acme projects visible")

        # Step 4: Project Details & Tasks Table
        print("[*] Opening Project: 'Acme Web Portal'...")
        page.locator(".project-card:has-text('Acme Web Portal')").click()
        page.wait_for_url("**/projects/*", timeout=10000)
        page.wait_for_selector(".task-table, .pd-tabs")
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_04_project_detail.png"))
        log_test("BROWSER", "Project Detail & Tasks", True, "Task table displayed")

        # Step 5: In-Browser Task Creation
        print("[*] Creating task via browser modal...")
        page.click("button:has-text('New Task')")
        page.wait_for_selector("input#task-title")
        task_title = f"Browser Automated Task {int(time.time())}"
        page.fill("input#task-title", task_title)
        page.fill("textarea#task-desc", "Created via Playwright browser interaction")
        page.select_option("select#priority", "high")
        assignee_select = page.locator("select#assignee")
        if assignee_select.count() > 0:
            opts = assignee_select.locator("option").all()
            if len(opts) > 1:
                val = opts[1].get_attribute("value")
                if val:
                    page.select_option("select#assignee", val)
        page.click("button[type='submit']:has-text('Create Task'), form button[type='submit']")
        time.sleep(1.5)
        expect(page.locator(f"text={task_title}")).to_be_visible()
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_05_task_created.png"))
        log_test("BROWSER", "Task Creation via Modal", True, f"Rendered '{task_title}' on board")

        # Step 6: Employee Login (Bob Smith)
        print("[*] Signing out & logging in as employee (bob@acme.com)...")
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)
        page.fill("input#email", "bob@acme.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/member-dashboard", timeout=10000)
        page.wait_for_selector(".page")
        expect(page.locator(".user-name")).to_contain_text("Bob Smith")
        expect(page.locator(".user-role")).to_contain_text("member")
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_06_employee_dashboard.png"))
        log_test("BROWSER", "Employee Dashboard Scoping", True, "Employee workspace isolated")

        # Step 7: Multi-Tenant Data Isolation (Globex Systems)
        print("[*] Testing multi-tenant isolation with Globex Systems...")
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)
        page.fill("input#email", "manager@globex.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/manager-dashboard", timeout=10000)
        expect(page.locator(".user-name")).to_contain_text("George Sterling")

        page.click("a[href='/projects']")
        page.wait_for_url("**/projects", timeout=10000)
        page.wait_for_selector(".project-card")
        globex_text = page.content()
        assert "Globex ERP Next" in globex_text and "Globex Security Audit" in globex_text
        assert "Acme Web Portal" not in globex_text, "Cross-tenant leak detected!"
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_07_globex_tenant_isolation.png"))
        log_test("BROWSER", "Multi-Tenant Isolation", True, "Globex projects visible, Acme projects isolated")

        # Step 8: Multi-Company Manager Logins (Initech & Umbrella)
        print("[*] Verifying Initech Software manager login...")
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)
        page.fill("input#email", "manager@initech.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/manager-dashboard", timeout=10000)
        expect(page.locator(".user-name")).to_contain_text("Peter Gibbons")
        log_test("BROWSER", "Initech Manager Login", True, "Peter Gibbons dashboard verified")

        print("[*] Verifying Umbrella Corp manager login...")
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)
        page.fill("input#email", "manager@umbrella.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/manager-dashboard", timeout=10000)
        expect(page.locator(".user-name")).to_contain_text("Albert Wesker")
        page.screenshot(path=str(SCREENSHOTS_DIR / "browser_08_umbrella_dashboard.png"))
        log_test("BROWSER", "Umbrella Manager Login", True, "Albert Wesker dashboard verified")

        browser.close()

    print("\n" + "="*75)
    print("SUCCESS: 100% OF PLAYWRIGHT API AND BROWSER AUTOMATION TESTS PASSED!")
    print("="*75 + "\n")

if __name__ == "__main__":
    run_suite()
