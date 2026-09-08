"""
seed.py – populate the database with a default admin user and sample data.
Run once after migrations: python seed.py
"""
import sys
import os
# Ensure the app package is importable when running as `python seed.py` from /app
sys.path.insert(0, os.path.dirname(__file__))
from app.db.migrations import ensure_user_organization_column
from app.db.session import Base, engine, SessionLocal
from app.models.models import GlobalRole, Project, ProjectMember, ProjectRole, Task, TaskPriority, TaskStatus, User
from app.core.security import hash_password 
DEFAULT_PASSWORD = "Admin1234!"  # Change via env var in production
ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@taskmanager.com")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", DEFAULT_PASSWORD)
DEFAULT_ORGANIZATION = os.getenv("SEED_ORGANIZATION_NAME", "TaskFlow")
def seed():
    Base.metadata.create_all(bind=engine)
    ensure_user_organization_column(engine)
    db = SessionLocal()
    try:
        # ── Admin user ────────────────────────────────────────────────────────
        admin = db.query(User).filter_by(email=ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=ADMIN_EMAIL,
                full_name="Admin User",
                organization_name=DEFAULT_ORGANIZATION,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=GlobalRole.ADMIN,
            )
            db.add(admin)
            db.flush()
            print(f"[seed] Created admin: {ADMIN_EMAIL}")
        else:
            if not admin.organization_name:
                admin.organization_name = DEFAULT_ORGANIZATION
            print(f"[seed] Admin already exists: {ADMIN_EMAIL} — skipping")
 
        # ── Sample member ─────────────────────────────────────────────────────
        member_email = "member@taskmanager.com"
        member = db.query(User).filter_by(email=member_email).first()
        if not member:
            member = User(
                email=member_email,
                full_name="Sample Member",
                organization_name=DEFAULT_ORGANIZATION,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=GlobalRole.MEMBER,
            )
            db.add(member)
            db.flush()
            print(f"[seed] Created member: {member_email}")
        elif not member.organization_name:
            member.organization_name = DEFAULT_ORGANIZATION
 
        # ── Sample project ────────────────────────────────────────────────────
        project = db.query(Project).filter_by(name="Demo Project").first()
        if not project:
            project = Project(name="Demo Project", description="Auto-seeded demo project")
            db.add(project)
            db.flush()
 
            # Admin is owner
            db.add(ProjectMember(project_id=project.id, user_id=admin.id, role=ProjectRole.OWNER))
            # Member joins as member
            db.add(ProjectMember(project_id=project.id, user_id=member.id, role=ProjectRole.MEMBER))
            db.flush()
 
            # Sample tasks
            db.add(Task(
                title="Set up CI/CD pipeline",
                description="Configure GitHub Actions for automated testing and deployment.",
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                project_id=project.id,
                creator_id=admin.id,
                assignee_id=member.id,
            ))
            db.add(Task(
                title="Write API documentation",
                description="Document all endpoints using OpenAPI spec.",
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.MEDIUM,
                project_id=project.id,
                creator_id=admin.id,
                assignee_id=member.id,
            ))
            print(f"[seed] Created project '{project.name}' with 2 tasks")
 
        db.commit()
        print("[seed] Done ✓")
 
    except Exception as exc:
        db.rollback()
        print(f"[seed] ERROR: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()
 
 
if __name__ == "__main__":
    seed()
