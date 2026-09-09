"""
Automated Playwright Browser E2E Test Suite for TaskFlow.
Tests real user journeys across multiple companies, roles (Manager vs Employee),
projects, tasks, and multi-tenant security isolation.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

# Reconfigure stdout for Windows console UTF-8 safety
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"

# Output directory for test screenshots
ARTIFACT_DIR = Path(r"C:\Users\Hp\.gemini\antigravity-ide\brain\a179b7ff-8076-49c0-93ef-04d188691b76")
SCREENSHOTS_DIR = ARTIFACT_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def run_playwright_tests():
    print("\n" + "="*70)
    print(">>> PLAYWRIGHT AUTOMATED BROWSER E2E TEST SUITE")
    print("="*70)

    with sync_playwright() as p:
        print("[*] Launching Chromium browser (headless mode)...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # -------------------------------------------------------------
        # 1. Test Landing & Login Page UI
        # -------------------------------------------------------------
        print("\n[Step 1] Navigating to Login Page...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_selector(".auth-card")
        
        expect(page.locator(".auth-brand")).to_contain_text("TaskFlow")
        expect(page.locator("h1")).to_contain_text("Welcome back")
        expect(page.locator("input#email")).to_be_visible()
        expect(page.locator("input#password")).to_be_visible()
        
        login_shot = SCREENSHOTS_DIR / "01_login_page.png"
        page.screenshot(path=str(login_shot))
        print(f"[PASS] Login Page loaded successfully. Saved screenshot: {login_shot.name}")

        # -------------------------------------------------------------
        # 2. Test Login as Company Manager (Acme Corp)
        # -------------------------------------------------------------
        print("\n[Step 2] Logging in as Acme Manager (manager@acme.com)...")
        page.fill("input#email", "manager@acme.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")

        page.wait_for_url("**/manager-dashboard", timeout=10000)
        page.wait_for_selector(".dash-stats")

        # Verify manager dashboard metrics
        expect(page.locator(".page-title")).to_contain_text("Dashboard")
        expect(page.locator(".user-name")).to_contain_text("Alice Vance")
        expect(page.locator(".user-role")).to_contain_text("admin")

        mgr_shot = SCREENSHOTS_DIR / "02_acme_manager_dashboard.png"
        page.screenshot(path=str(mgr_shot))
        print(f"[PASS] Manager Dashboard verified. Saved screenshot: {mgr_shot.name}")

        # -------------------------------------------------------------
        # 3. Test Navigation to Projects
        # -------------------------------------------------------------
        print("\n[Step 3] Navigating to Projects Page...")
        page.click("a[href='/projects']")
        page.wait_for_url("**/projects", timeout=10000)
        page.wait_for_selector(".project-card")
        time.sleep(1)

        # Check for Acme projects in UI
        expect(page.locator(".page-title")).to_contain_text("Projects")
        page_content = page.content()
        assert "Acme Web Portal" in page_content, "Expected 'Acme Web Portal' to be present"
        assert "Acme Mobile App" in page_content, "Expected 'Acme Mobile App' to be present"
        assert "Acme Cloud Infrastructure" in page_content, "Expected 'Acme Cloud Infrastructure' to be present"

        proj_shot = SCREENSHOTS_DIR / "03_acme_projects_page.png"
        page.screenshot(path=str(proj_shot))
        print(f"[PASS] Acme projects listed (Web Portal, Mobile App, Cloud Infra). Saved screenshot: {proj_shot.name}")

        # -------------------------------------------------------------
        # 4. Open Project Detail and Inspect Tasks Board
        # -------------------------------------------------------------
        print("\n[Step 4] Opening Project: 'Acme Web Portal'...")
        page.locator(".project-card:has-text('Acme Web Portal')").click()
        page.wait_for_url("**/projects/*", timeout=10000)
        page.wait_for_selector(".task-table, .pd-tabs")
        time.sleep(1)

        detail_shot = SCREENSHOTS_DIR / "04_acme_project_detail_board.png"
        page.screenshot(path=str(detail_shot))
        print(f"[PASS] Project detail view & tasks table loaded. Saved screenshot: {detail_shot.name}")

        # -------------------------------------------------------------
        # 5. Create a New Task via Browser UI
        # -------------------------------------------------------------
        print("\n[Step 5] Creating a new task via UI modal...")
        page.click("button:has-text('New Task')")
        page.wait_for_selector("input#task-title")

        test_title = f"Playwright Verification Task {int(time.time())}"
        page.fill("input#task-title", test_title)
        page.fill("textarea#task-desc", "Created by automated Playwright browser test.")
        page.select_option("select#priority", "high")
        
        # Select first available employee in dropdown if present
        assignee_select = page.locator("select#assignee")
        if assignee_select.count() > 0:
            options = assignee_select.locator("option").all()
            if len(options) > 1:
                val = options[1].get_attribute("value")
                if val:
                    page.select_option("select#assignee", val)

        page.click("button[type='submit']:has-text('Create Task'), form button[type='submit']")
        time.sleep(1.5)

        # Check task appears in table
        expect(page.locator(f"text={test_title}")).to_be_visible()
        task_created_shot = SCREENSHOTS_DIR / "05_new_task_created.png"
        page.screenshot(path=str(task_created_shot))
        print(f"[PASS] New task successfully created and rendered in table. Saved screenshot: {task_created_shot.name}")

        # -------------------------------------------------------------
        # 6. Test Employee Login & Scoped Permissions (Bob Smith)
        # -------------------------------------------------------------
        print("\n[Step 6] Testing Sign Out & Login as Employee (bob@acme.com)...")
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)

        page.fill("input#email", "bob@acme.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")

        page.wait_for_url("**/member-dashboard", timeout=10000)
        page.wait_for_selector(".page")
        time.sleep(1)

        expect(page.locator(".user-name")).to_contain_text("Bob Smith")
        expect(page.locator(".user-role")).to_contain_text("member")

        emp_shot = SCREENSHOTS_DIR / "06_employee_dashboard.png"
        page.screenshot(path=str(emp_shot))
        print(f"[PASS] Employee dashboard loaded with member role. Saved screenshot: {emp_shot.name}")

        # -------------------------------------------------------------
        # 7. Test Multi-Company Multi-Tenant Isolation (Globex Systems)
        # -------------------------------------------------------------
        print("\n[Step 7] Testing Multi-Tenant Isolation with Globex Systems Manager...")
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)

        page.fill("input#email", "manager@globex.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")

        page.wait_for_url("**/manager-dashboard", timeout=10000)
        expect(page.locator(".user-name")).to_contain_text("George Sterling")

        # Navigate to Projects and ensure ONLY Globex projects are shown
        page.click("a[href='/projects']")
        page.wait_for_url("**/projects", timeout=10000)
        page.wait_for_selector(".project-card")
        time.sleep(1)

        globex_content = page.content()
        assert "Globex ERP Next" in globex_content, "Expected 'Globex ERP Next' to be present"
        assert "Globex Security Audit" in globex_content, "Expected 'Globex Security Audit' to be present"
        assert "Acme Web Portal" not in globex_content, "Tenant leak! Globex must not see Acme projects"

        globex_shot = SCREENSHOTS_DIR / "07_globex_tenant_isolation.png"
        page.screenshot(path=str(globex_shot))
        print(f"[PASS] Multi-tenant data isolation verified. Globex projects visible, Acme projects isolated. Screenshot: {globex_shot.name}")

        # -------------------------------------------------------------
        # 8. Test Initech Software & Umbrella Corp Accounts Login
        # -------------------------------------------------------------
        print("\n[Step 8] Verifying Initech Software and Umbrella Corp manager logins...")
        # Initech
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)
        page.fill("input#email", "manager@initech.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/manager-dashboard", timeout=10000)
        expect(page.locator(".user-name")).to_contain_text("Peter Gibbons")
        print("  [+] Initech manager (Peter Gibbons) verified.")

        # Umbrella Corp
        page.click(".logout-btn, button:has-text('Sign out')")
        page.wait_for_url("**/login", timeout=10000)
        page.fill("input#email", "manager@umbrella.com")
        page.fill("input#password", "Test@Password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/manager-dashboard", timeout=10000)
        expect(page.locator(".user-name")).to_contain_text("Albert Wesker")
        print("  [+] Umbrella manager (Albert Wesker) verified.")

        umbrella_shot = SCREENSHOTS_DIR / "08_umbrella_manager_dashboard.png"
        page.screenshot(path=str(umbrella_shot))
        print(f"[PASS] Umbrella Corp manager dashboard verified. Screenshot: {umbrella_shot.name}")

        browser.close()

    print("\n" + "="*70)
    print("SUCCESS: ALL PLAYWRIGHT AUTOMATED BROWSER TESTS PASSED!")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_playwright_tests()
