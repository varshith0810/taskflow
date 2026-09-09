"""
TaskFlow – Database Seeder
Seeds initial roles, demo users, projects, project memberships, and tasks.
Safe to run in dev/staging; guarded against accidental execution in production.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure stdout/stderr handles Unicode safely on Windows
for stream in (sys.stdout, sys.stderr):
    reconfig = getattr(stream, "reconfigure", None)
    if callable(reconfig):
        try:
            reconfig(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Ensure parent directory is in sys.path when executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.core.security import hash_password, get_password_hash
from app.db.migrations import ensure_user_organization_column
from app.db.session import Base, SessionLocal, engine
from app.models.models import (
    GlobalRole,
    Project,
    ProjectMember,
    ProjectRole,
    Task,
    TaskPriority,
    TaskStatus,
    User,
)


# ── Production Safety Guard ───────────────────────────────────────────────────
def check_environment_guard() -> None:
    environment = os.getenv("ENVIRONMENT", "development").lower()
    enable_seed = os.getenv("ENABLE_SEED", "false").lower() in ("true", "1", "yes")

    if environment == "production" and not enable_seed:
        print("[seed] ENVIRONMENT=production detected: skipping database seeding.")
        print("       (Set ENABLE_SEED=true if you explicitly want to run seeds in production).")
        sys.exit(0)


# ── Seeder Logic ─────────────────────────────────────────────────────────────
def seed_database() -> None:
    check_environment_guard()

    print("[seed] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    ensure_user_organization_column(engine)

    db = SessionLocal()

    try:
        print("[seed] Seeding database...")

        # 1. Seed Users (Idempotent)
        admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin@123456")
        default_user_password = os.getenv("SEED_USER_PASSWORD", "User@123456")

        users_data = [
            {
                "email": "admin@taskflow.dev",
                "full_name": "Sarah Connor (Admin)",
                "role": GlobalRole.ADMIN,
                "organization_name": "TaskFlow Core",
                "password": admin_password,
            },
            {
                "email": "alex.pm@taskflow.dev",
                "full_name": "Alex Mercer (Product Manager)",
                "role": GlobalRole.MEMBER,
                "organization_name": "TaskFlow Core",
                "password": default_user_password,
            },
            {
                "email": "dev.jordan@taskflow.dev",
                "full_name": "Jordan Lee (Fullstack Dev)",
                "role": GlobalRole.MEMBER,
                "organization_name": "TaskFlow Core",
                "password": default_user_password,
            },
            {
                "email": "qa.elena@taskflow.dev",
                "full_name": "Elena Rostova (QA Engineer)",
                "role": GlobalRole.MEMBER,
                "organization_name": "TaskFlow Core",
                "password": default_user_password,
            },
        ]

        seeded_users: dict[str, User] = {}
        for u in users_data:
            existing_user = db.query(User).filter(User.email == u["email"]).first()
            if not existing_user:
                new_user = User(
                    email=u["email"],
                    full_name=u["full_name"],
                    role=u["role"],
                    organization_name=u["organization_name"],
                    hashed_password=hash_password(u["password"]),
                    is_active=True,
                )
                db.add(new_user)
                db.flush()  # populate new_user.id
                seeded_users[u["email"]] = new_user
                print(f"  [+] Created user: {u['email']} [{u['role'].value}]")
            else:
                if not existing_user.organization_name:
                    existing_user.organization_name = u["organization_name"]
                seeded_users[u["email"]] = existing_user
                print(f"  [.] User already exists: {u['email']}")

        admin_user = seeded_users.get("admin@taskflow.dev")
        pm_user = seeded_users.get("alex.pm@taskflow.dev")
        dev_user = seeded_users.get("dev.jordan@taskflow.dev")
        qa_user = seeded_users.get("qa.elena@taskflow.dev")

        # 2. Seed Projects & Project Members (Idempotent)
        projects_data = [
            {
                "name": "AWS Cloud Migration",
                "description": "Migrate TaskFlow backend and database to AWS App Runner and RDS.",
                "members": [
                    (admin_user, ProjectRole.OWNER),
                    (pm_user, ProjectRole.MANAGER),
                    (dev_user, ProjectRole.MEMBER),
                    (qa_user, ProjectRole.MEMBER),
                ],
            },
            {
                "name": "Mobile Responsive UI",
                "description": "Modernize the React frontend for tablets and mobile devices.",
                "members": [
                    (admin_user, ProjectRole.OWNER),
                    (pm_user, ProjectRole.MANAGER),
                    (dev_user, ProjectRole.MEMBER),
                    (qa_user, ProjectRole.MEMBER),
                ],
            },
        ]

        seeded_projects: dict[str, Project] = {}
        for p in projects_data:
            existing_project = db.query(Project).filter(Project.name == p["name"]).first()
            if not existing_project:
                new_project = Project(
                    name=p["name"],
                    description=p["description"],
                    is_active=True,
                )
                db.add(new_project)
                db.flush()

                # Add project memberships
                for user_obj, proj_role in p["members"]:
                    if user_obj:
                        db.add(
                            ProjectMember(
                                project_id=new_project.id,
                                user_id=user_obj.id,
                                role=proj_role,
                            )
                        )
                db.flush()

                seeded_projects[p["name"]] = new_project
                print(f"  [+] Created project: '{p['name']}' with members")
            else:
                # Ensure memberships exist for existing project
                for user_obj, proj_role in p["members"]:
                    if user_obj:
                        membership = (
                            db.query(ProjectMember)
                            .filter_by(project_id=existing_project.id, user_id=user_obj.id)
                            .first()
                        )
                        if not membership:
                            db.add(
                                ProjectMember(
                                    project_id=existing_project.id,
                                    user_id=user_obj.id,
                                    role=proj_role,
                                )
                            )
                db.flush()
                seeded_projects[p["name"]] = existing_project
                print(f"  [.] Project already exists: '{p['name']}'")

        p1 = seeded_projects.get("AWS Cloud Migration")
        p2 = seeded_projects.get("Mobile Responsive UI")

        # 3. Seed Tasks (Idempotent)
        now = datetime.now(timezone.utc)
        tasks_data = [
            # Tasks for Project 1
            {
                "title": "Configure AWS RDS PostgreSQL Database",
                "description": "Create db.t4g.micro instance on AWS RDS and verify 5432 security group rules.",
                "status": TaskStatus.DONE,
                "priority": TaskPriority.HIGH,
                "project_id": p1.id if p1 else None,
                "creator_id": admin_user.id if admin_user else None,
                "assignee_id": admin_user.id if admin_user else None,
                "due_date": now + timedelta(days=2),
            },
            {
                "title": "Deploy Container on AWS App Runner",
                "description": "Connect GitHub repo, configure environment variables, and verify /health check.",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.CRITICAL,
                "project_id": p1.id if p1 else None,
                "creator_id": admin_user.id if admin_user else None,
                "assignee_id": dev_user.id if dev_user else None,
                "due_date": now + timedelta(days=4),
            },
            {
                "title": "End-to-End Smoke Testing",
                "description": "Validate user login, token refresh, and task CRUD operations on live AWS URL.",
                "status": TaskStatus.TODO,
                "priority": TaskPriority.MEDIUM,
                "project_id": p1.id if p1 else None,
                "creator_id": pm_user.id if pm_user else None,
                "assignee_id": qa_user.id if qa_user else None,
                "due_date": now + timedelta(days=7),
            },
            # Tasks for Project 2
            {
                "title": "Audit Mobile Viewport Breakpoints",
                "description": "Fix navigation drawer and table overflow on viewport widths below 768px.",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.HIGH,
                "project_id": p2.id if p2 else None,
                "creator_id": pm_user.id if pm_user else None,
                "assignee_id": dev_user.id if dev_user else None,
                "due_date": now + timedelta(days=3),
            },
            {
                "title": "Touch Gesture Optimization",
                "description": "Implement swipe gestures for dragging task cards between columns.",
                "status": TaskStatus.TODO,
                "priority": TaskPriority.LOW,
                "project_id": p2.id if p2 else None,
                "creator_id": pm_user.id if pm_user else None,
                "assignee_id": dev_user.id if dev_user else None,
                "due_date": now + timedelta(days=10),
            },
        ]

        for t in tasks_data:
            if not t["project_id"]:
                continue
            existing_task = (
                db.query(Task)
                .filter(Task.title == t["title"], Task.project_id == t["project_id"])
                .first()
            )
            if not existing_task:
                new_task = Task(
                    title=t["title"],
                    description=t["description"],
                    status=t["status"],
                    priority=t["priority"],
                    project_id=t["project_id"],
                    creator_id=t["creator_id"],
                    assignee_id=t["assignee_id"],
                    due_date=t["due_date"],
                )
                db.add(new_task)
                print(f"  [+] Created task: '{t['title']}' [{t['status'].value.upper()}]")
            else:
                print(f"  [.] Task already exists: '{t['title']}'")

        db.commit()
        print("\n[OK] Database seeding completed successfully!")
        print("--------------------------------------------------")
        print("Demo Credentials for Local Testing:")
        print(f"  * Admin:   admin@taskflow.dev   /  {admin_password}")
        print(f"  * Manager: alex.pm@taskflow.dev  /  {default_user_password}")
        print(f"  * Member:  dev.jordan@taskflow.dev / {default_user_password}")
        print(f"  * QA:      qa.elena@taskflow.dev   / {default_user_password}")
        print("--------------------------------------------------\n")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error while seeding database: {e}", file=sys.stderr)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()