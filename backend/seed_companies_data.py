"""
Seed script to generate:
- 4 Companies
- 20 Users (5 per company: 1 Manager [Admin], 4 Employees [Member])
- 3 Projects per company (12 Projects total)
- 2 Employees assigned to each project
- At least 3 tasks per employee per project (6+ tasks per project, 72+ tasks total)
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure stdout handles UTF-8 cleanly
for stream in (sys.stdout, sys.stderr):
    reconfig = getattr(stream, "reconfigure", None)
    if callable(reconfig):
        try:
            reconfig(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.security import hash_password
from app.db.session import SessionLocal, engine, Base
from app.models.models import (
    User, GlobalRole, Project, ProjectMember, ProjectRole,
    Task, TaskStatus, TaskPriority
)

PASSWORD = "Test@Password123"

COMPANIES = [
    {
        "name": "Acme Corp",
        "manager": {"email": "manager@acme.com", "name": "Alice Vance (Manager)"},
        "employees": [
            {"email": "bob@acme.com", "name": "Bob Smith"},
            {"email": "charlie@acme.com", "name": "Charlie Brown"},
            {"email": "david@acme.com", "name": "David Miller"},
            {"email": "emma@acme.com", "name": "Emma Wilson"},
        ],
        "projects": [
            {
                "name": "Acme Web Portal",
                "desc": "Modern responsive customer web portal",
                "assigned_emp_indices": [0, 1],  # Bob, Charlie
                "tasks_emp_a": [
                    ("Build Navigation & Header Component", "Create responsive mobile navigation menu", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Integrate Authentication State", "Connect login/signup state with tokens", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Unit Test Navbar Component", "Write unit tests for desktop & mobile navbar", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
                "tasks_emp_b": [
                    ("Setup Tailwind / CSS Design Tokens", "Establish color variables, fonts, and dark mode tokens", TaskStatus.DONE, TaskPriority.MEDIUM),
                    ("Implement User Profile Form", "Build editable user profile and avatar upload", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Validate Accessibility & ARIA labels", "Run axe-core scan on portal pages", TaskStatus.TODO, TaskPriority.LOW),
                ],
            },
            {
                "name": "Acme Mobile App",
                "desc": "Cross-platform mobile application",
                "assigned_emp_indices": [2, 3],  # David, Emma
                "tasks_emp_a": [
                    ("Configure Push Notifications", "Integrate FCM push notification service", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Offline Cache Storage", "Implement local SQLite caching for offline mode", TaskStatus.TODO, TaskPriority.CRITICAL),
                    ("Biometric Login Integration", "Add FaceID and fingerprint authentication", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
                "tasks_emp_b": [
                    ("Design App Splash & Onboarding", "Create introductory slides for first-time users", TaskStatus.DONE, TaskPriority.MEDIUM),
                    ("Optimize Bundle Asset Sizes", "Compress images and enable Hermes bytecode", TaskStatus.IN_PROGRESS, TaskPriority.LOW),
                    ("Deep Linking Implementation", "Support universal links for project shares", TaskStatus.TODO, TaskPriority.HIGH),
                ],
            },
            {
                "name": "Acme Cloud Infrastructure",
                "desc": "Kubernetes migration and CI/CD pipelines",
                "assigned_emp_indices": [0, 3],  # Bob, Emma
                "tasks_emp_a": [
                    ("Write Helm Charts", "Define deployment, service, and ingress manifests", TaskStatus.DONE, TaskPriority.CRITICAL),
                    ("Setup Prometheus Monitoring", "Configure node exporter and Grafana dashboards", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Configure Autoscaling Policies", "Set HPA thresholds for CPU and memory spikes", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
                "tasks_emp_b": [
                    ("Create GitHub Actions CI/CD", "Automate linting, unit tests, and image push", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Security Hardening & Secret Rotation", "Integrate Vault for dynamic database credentials", TaskStatus.IN_PROGRESS, TaskPriority.CRITICAL),
                    ("Disaster Recovery Plan Drill", "Document backup restoration procedure", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
            },
        ],
    },
    {
        "name": "Globex Systems",
        "manager": {"email": "manager@globex.com", "name": "George Sterling (Manager)"},
        "employees": [
            {"email": "grace@globex.com", "name": "Grace Hopper"},
            {"email": "hank@globex.com", "name": "Hank Pym"},
            {"email": "ivy@globex.com", "name": "Ivy Chen"},
            {"email": "jack@globex.com", "name": "Jack Ryan"},
        ],
        "projects": [
            {
                "name": "Globex ERP Next",
                "desc": "Enterprise resource planning platform",
                "assigned_emp_indices": [0, 1],  # Grace, Hank
                "tasks_emp_a": [
                    ("Invoice PDF Generation Module", "Generate branded tax invoices in PDF format", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Stripe & PayPal Gateway", "Handle webhook callbacks and subscription renewals", TaskStatus.IN_PROGRESS, TaskPriority.CRITICAL),
                    ("Multi-Currency Conversion Service", "Fetch live exchange rates daily", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
                "tasks_emp_b": [
                    ("Inventory Stock Tracking", "Real-time warehouse SKU decrement on checkout", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Supplier Portal Authentication", "Allow vendors to update purchase orders", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM),
                    ("Audit Logging Middleware", "Track financial record modifications", TaskStatus.TODO, TaskPriority.HIGH),
                ],
            },
            {
                "name": "Globex Security Audit",
                "desc": "SOC2 and ISO 27001 compliance hardening",
                "assigned_emp_indices": [2, 3],  # Ivy, Jack
                "tasks_emp_a": [
                    ("Penetration Testing Scope", "Scan API endpoints for OWASP Top 10 vulnerabilities", TaskStatus.IN_PROGRESS, TaskPriority.CRITICAL),
                    ("Rotate TLS Certificates", "Automate Let's Encrypt renewal with certbot", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Database Encryption At Rest", "Enable AES-256 transparent data encryption", TaskStatus.TODO, TaskPriority.HIGH),
                ],
                "tasks_emp_b": [
                    ("IAM Policy Least Privilege Review", "Audit cloud roles and remove wildcards", TaskStatus.DONE, TaskPriority.MEDIUM),
                    ("Security Awareness Training Docs", "Compile developer guidelines for safe coding", TaskStatus.TODO, TaskPriority.LOW),
                    ("Incident Response Runbook", "Define severity 1 escalation paths and paging", TaskStatus.TODO, TaskPriority.HIGH),
                ],
            },
            {
                "name": "Globex Analytics Pipeline",
                "desc": "Real-time streaming telemetry and analytics",
                "assigned_emp_indices": [0, 2],  # Grace, Ivy
                "tasks_emp_a": [
                    ("Kafka Event Topic Setup", "Partition user engagement events across brokers", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Clickhouse Schema Optimization", "Define table engines with compression codecs", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Aggregated Metrics Materialized View", "Pre-calculate hourly active users and retention", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
                "tasks_emp_b": [
                    ("Real-time Dashboard Graphs", "Render live throughput gauges with WebSockets", TaskStatus.DONE, TaskPriority.MEDIUM),
                    ("Anomaly Detection Alert Rules", "Alert on 3x standard deviation error spikes", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Data Retention Archival Job", "Cold-store 90+ day logs into S3 Glacier", TaskStatus.TODO, TaskPriority.LOW),
                ],
            },
        ],
    },
    {
        "name": "Initech Software",
        "manager": {"email": "manager@initech.com", "name": "Peter Gibbons (Manager)"},
        "employees": [
            {"email": "milton@initech.com", "name": "Milton Waddams"},
            {"email": "samir@initech.com", "name": "Samir Nagheenanajar"},
            {"email": "michael@initech.com", "name": "Michael Bolton"},
            {"email": "joanna@initech.com", "name": "Joanna Clark"},
        ],
        "projects": [
            {
                "name": "Initech TPS Report Engine",
                "desc": "Automated corporate reporting and compliance system",
                "assigned_emp_indices": [0, 1],  # Milton, Samir
                "tasks_emp_a": [
                    ("Design New Cover Sheet Template", "Ensure all TPS reports have mandatory cover sheets", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Automated Email Distribution", "Email weekly executive summaries every Friday", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM),
                    ("Fix Printer Spooler Bug", "Resolve paper jam and toner communication error", TaskStatus.TODO, TaskPriority.CRITICAL),
                ],
                "tasks_emp_b": [
                    ("Build Excel Export Engine", "Export multi-sheet spreadsheets with styling", TaskStatus.DONE, TaskPriority.MEDIUM),
                    ("Role-Based Approval Workflow", "Require manager signoff before filing", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Archive Legacy TPS Formats", "Migrate 2010 file formats to modern schema", TaskStatus.TODO, TaskPriority.LOW),
                ],
            },
            {
                "name": "Initech Accounting Modernization",
                "desc": "High precision financial calculation service",
                "assigned_emp_indices": [2, 3],  # Michael, Joanna
                "tasks_emp_a": [
                    ("Floating Point Rounding Precision", "Enforce fixed decimal precision on transactions", TaskStatus.DONE, TaskPriority.CRITICAL),
                    ("Reconcile Bank Statements", "Automate matching of daily debit/credit records", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Tax Calculation API Integration", "Support jurisdictional VAT and sales taxes", TaskStatus.TODO, TaskPriority.HIGH),
                ],
                "tasks_emp_b": [
                    ("Payroll Direct Deposit Sync", "Batch generate ACH files for employee deposits", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Expense Reimbursement Workflow", "Allow receipt attachment uploads and optical scan", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM),
                    ("Quarterly Ledger Closing Scripts", "Lock fiscal periods upon audit signoff", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
            },
            {
                "name": "Initech Customer Portal",
                "desc": "Self-service support and billing dashboard",
                "assigned_emp_indices": [0, 3],  # Milton, Joanna
                "tasks_emp_a": [
                    ("Knowledge Base Search Filter", "Implement full-text search with highlighting", TaskStatus.DONE, TaskPriority.MEDIUM),
                    ("Ticket Priority Escalation Bot", "Auto-route high severity issues to on-call", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Customer Satisfaction Survey Modal", "Prompt CSAT feedback after resolution", TaskStatus.TODO, TaskPriority.LOW),
                ],
                "tasks_emp_b": [
                    ("Single Sign-On (SAML/Okta)", "Support enterprise customer identity providers", TaskStatus.DONE, TaskPriority.CRITICAL),
                    ("Subscription Upgrade Checkout", "Provide tiered plan selection with pro-rating", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Usage Quota Warning Banners", "Display usage percentage and upsell prompt", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
            },
        ],
    },
    {
        "name": "Umbrella Corp",
        "manager": {"email": "manager@umbrella.com", "name": "Albert Wesker (Manager)"},
        "employees": [
            {"email": "jill@umbrella.com", "name": "Jill Valentine"},
            {"email": "chris@umbrella.com", "name": "Chris Redfield"},
            {"email": "leon@umbrella.com", "name": "Leon Kennedy"},
            {"email": "claire@umbrella.com", "name": "Claire Redfield"},
        ],
        "projects": [
            {
                "name": "Umbrella Bio-Research Hub",
                "desc": "Genomic sequence sequencing and analysis pipeline",
                "assigned_emp_indices": [0, 1],  # Jill, Chris
                "tasks_emp_a": [
                    ("FastQ Sequence Ingestion Worker", "Stream raw DNA read files into processing queue", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Variant Annotation Pipeline", "Cross-reference NCBI and dbSNP databases", TaskStatus.IN_PROGRESS, TaskPriority.CRITICAL),
                    ("Phylogenetic Tree Visualization", "Render interactive cladogram in WebGL", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
                "tasks_emp_b": [
                    ("Lab Equipment IoT Telemetry", "Monitor centrifuge RPM and freezer temperatures", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Sample Barcode Scanner API", "Scan 2D DataMatrix barcodes on test vials", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Hazardous Material Tracking Report", "Generate bi-weekly biosafety level compliance", TaskStatus.TODO, TaskPriority.CRITICAL),
                ],
            },
            {
                "name": "Umbrella Facility Access Control",
                "desc": "Biometric door lock and visitor monitoring system",
                "assigned_emp_indices": [2, 3],  # Leon, Claire
                "tasks_emp_a": [
                    ("RFID Keycard Reader Interface", "Low latency badge verification over RS-485", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Emergency Lockdown Override", "Centralized switch to seal blast doors", TaskStatus.IN_PROGRESS, TaskPriority.CRITICAL),
                    ("CCTV Facial Recognition Stream", "Flag unauthorized personnel in restricted zones", TaskStatus.TODO, TaskPriority.HIGH),
                ],
                "tasks_emp_b": [
                    ("Visitor Badge Printing Station", "Take visitor photo and print thermal pass", TaskStatus.DONE, TaskPriority.LOW),
                    ("Guard Patrol Checkpoint App", "NFC tap route logging for security personnel", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM),
                    ("Automated Fire Suppression Test", "Verify Halon release triggers and sensor logs", TaskStatus.TODO, TaskPriority.HIGH),
                ],
            },
            {
                "name": "Umbrella Logistics Network",
                "desc": "Cold-chain pharmaceutical delivery and drone routing",
                "assigned_emp_indices": [0, 3],  # Jill, Claire
                "tasks_emp_a": [
                    ("GPS Fleet Telematics Dashboard", "Show real-time refrigerated truck locations", TaskStatus.DONE, TaskPriority.HIGH),
                    ("Dry Ice Temperature Loggers", "Alert when dry ice levels drop below -70C", TaskStatus.IN_PROGRESS, TaskPriority.CRITICAL),
                    ("Route Optimization Engine", "Calculate fastest delivery path avoiding traffic", TaskStatus.TODO, TaskPriority.MEDIUM),
                ],
                "tasks_emp_b": [
                    ("Warehouse Drone Dispatch API", "Automate high-rack inventory picking", TaskStatus.DONE, TaskPriority.MEDIUM),
                    ("Customs Clearance Documents", "Auto-generate international manifests", TaskStatus.IN_PROGRESS, TaskPriority.HIGH),
                    ("Proof of Delivery Signature Capture", "Collect digital recipient signature on glass", TaskStatus.TODO, TaskPriority.LOW),
                ],
            },
        ],
    },
]

def seed():
    print("[*] Connecting to database and seeding 4 companies with 20 users, 12 projects, and 72 tasks...")
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    total_users_created = 0
    total_projects_created = 0
    total_tasks_created = 0

    try:
        for comp in COMPANIES:
            org_name = comp["name"]
            print(f"\n=======================================================")
            print(f"🏢 Company: {org_name}")
            print(f"=======================================================")

            # 1. Create or get Manager
            mgr_info = comp["manager"]
            manager = db.query(User).filter_by(email=mgr_info["email"]).first()
            if not manager:
                manager = User(
                    email=mgr_info["email"],
                    full_name=mgr_info["name"],
                    organization_name=org_name,
                    hashed_password=hash_password(PASSWORD),
                    role=GlobalRole.ADMIN,
                    is_active=True,
                )
                db.add(manager)
                db.flush()
                total_users_created += 1
                print(f"  [+] Manager created: {manager.full_name} ({manager.email})")
            else:
                manager.organization_name = org_name
                print(f"  [.] Manager exists: {manager.email}")

            # 2. Create or get 4 Employees
            employees = []
            for emp_info in comp["employees"]:
                emp = db.query(User).filter_by(email=emp_info["email"]).first()
                if not emp:
                    emp = User(
                        email=emp_info["email"],
                        full_name=emp_info["name"],
                        organization_name=org_name,
                        hashed_password=hash_password(PASSWORD),
                        role=GlobalRole.MEMBER,
                        is_active=True,
                    )
                    db.add(emp)
                    db.flush()
                    total_users_created += 1
                    print(f"  [+] Employee created: {emp.full_name} ({emp.email})")
                else:
                    emp.organization_name = org_name
                    print(f"  [.] Employee exists: {emp.email}")
                employees.append(emp)

            # 3. Create 3 Projects
            for proj_info in comp["projects"]:
                proj_name = proj_info["name"]
                project = db.query(Project).filter_by(name=proj_name).first()
                if not project:
                    project = Project(
                        name=proj_name,
                        description=proj_info["desc"],
                        is_active=True,
                    )
                    db.add(project)
                    db.flush()
                    total_projects_created += 1
                    print(f"    [+] Project: '{proj_name}'")
                else:
                    print(f"    [.] Project exists: '{proj_name}'")

                # Ensure Manager is Owner of project
                mgr_member = db.query(ProjectMember).filter_by(project_id=project.id, user_id=manager.id).first()
                if not mgr_member:
                    db.add(ProjectMember(project_id=project.id, user_id=manager.id, role=ProjectRole.OWNER))
                    db.flush()

                # Assign the 2 designated employees to project
                idx_a, idx_b = proj_info["assigned_emp_indices"]
                emp_a = employees[idx_a]
                emp_b = employees[idx_b]

                for emp in (emp_a, emp_b):
                    emp_member = db.query(ProjectMember).filter_by(project_id=project.id, user_id=emp.id).first()
                    if not emp_member:
                        db.add(ProjectMember(project_id=project.id, user_id=emp.id, role=ProjectRole.MEMBER))
                        db.flush()
                        print(f"        -> Member added: {emp.full_name}")

                # Create 3 tasks for Employee A
                for title, desc, status, priority in proj_info["tasks_emp_a"]:
                    task = db.query(Task).filter_by(title=title, project_id=project.id).first()
                    if not task:
                        task = Task(
                            title=title,
                            description=desc,
                            status=status,
                            priority=priority,
                            project_id=project.id,
                            creator_id=manager.id,
                            assignee_id=emp_a.id,
                            due_date=now + timedelta(days=5),
                        )
                        db.add(task)
                        total_tasks_created += 1

                # Create 3 tasks for Employee B
                for title, desc, status, priority in proj_info["tasks_emp_b"]:
                    task = db.query(Task).filter_by(title=title, project_id=project.id).first()
                    if not task:
                        task = Task(
                            title=title,
                            description=desc,
                            status=status,
                            priority=priority,
                            project_id=project.id,
                            creator_id=manager.id,
                            assignee_id=emp_b.id,
                            due_date=now + timedelta(days=7),
                        )
                        db.add(task)
                        total_tasks_created += 1

        db.commit()
        print("\n=======================================================")
        print("🎉 Successfully completed database seeding!")
        print(f"   Companies       : {len(COMPANIES)}")
        print(f"   Users           : 20 (4 Managers + 16 Employees)")
        print(f"   Projects        : 12 (3 per company)")
        print(f"   Tasks Created   : 72 (3 per employee per project)")
        print(f"   Common Password : {PASSWORD}")
        print("=======================================================\n")

    except Exception as e:
        db.rollback()
        print(f"[!] Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
