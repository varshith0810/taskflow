import sys
sys.path.insert(0, "backend")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app
from app.models.models import GlobalRole, Project, ProjectMember, ProjectRole, User
from app.core.security import hash_password, create_access_token

# In-memory test database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

app = create_app()
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_project_crud_and_members():
    # Setup test users
    db = TestingSessionLocal()
    admin = User(
        email="admin@corp.com",
        full_name="Admin User",
        organization_name="Corp",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.ADMIN,
        is_active=True,
    )
    emp1 = User(
        email="emp1@corp.com",
        full_name="Employee One",
        organization_name="Corp",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.MEMBER,
        is_active=True,
    )
    emp2 = User(
        email="emp2@corp.com",
        full_name="Employee Two",
        organization_name="Corp",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.MEMBER,
        is_active=True,
    )
    other_org_user = User(
        email="other@other.com",
        full_name="Other User",
        organization_name="Other",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.MEMBER,
        is_active=True,
    )
    db.add_all([admin, emp1, emp2, other_org_user])
    db.commit()
    db.refresh(admin)
    db.refresh(emp1)
    db.refresh(emp2)
    db.refresh(other_org_user)

    admin_token = create_access_token(admin.id)
    emp1_token = create_access_token(emp1.id)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    emp1_headers = {"Authorization": f"Bearer {emp1_token}"}

    # 1. Test create project with member_ids (verifies fix for payload.model_dump bug)
    res = client.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={
            "name": "Project Alpha",
            "description": "First project",
            "member_ids": [emp1.id],
        },
    )
    assert res.status_code == 201, res.text
    proj_data = res.json()
    proj_id = proj_data["id"]
    assert proj_data["name"] == "Project Alpha"

    # 2. Test get project detail
    res = client.get(f"/api/v1/projects/{proj_id}", headers=admin_headers)
    assert res.status_code == 200, res.text
    detail = res.json()
    assert detail["task_count"] == 0
    assert len(detail["members"]) == 2  # Admin (owner) + emp1 (member)

    # 3. Test list projects for member
    res = client.get("/api/v1/projects", headers=emp1_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 4. Test add member
    res = client.post(
        f"/api/v1/projects/{proj_id}/members",
        headers=admin_headers,
        json={"user_id": emp2.id, "role": "member"},
    )
    assert res.status_code == 201
    assert res.json()["user_id"] == emp2.id

    # Test adding user from another org should fail
    res = client.post(
        f"/api/v1/projects/{proj_id}/members",
        headers=admin_headers,
        json={"user_id": other_org_user.id, "role": "member"},
    )
    assert res.status_code == 400

    # 5. Test update member role
    res = client.patch(
        f"/api/v1/projects/{proj_id}/members/{emp1.id}",
        headers=admin_headers,
        json={"role": "manager"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "manager"

    # Test cannot demote last owner
    res = client.patch(
        f"/api/v1/projects/{proj_id}/members/{admin.id}",
        headers=admin_headers,
        json={"role": "member"},
    )
    assert res.status_code == 400

    # 6. Test update project
    res = client.patch(
        f"/api/v1/projects/{proj_id}",
        headers=admin_headers,
        json={"name": "Project Alpha Updated"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Project Alpha Updated"

    # 7. Test remove member
    res = client.delete(
        f"/api/v1/projects/{proj_id}/members/{emp2.id}",
        headers=admin_headers,
    )
    assert res.status_code == 204

    # 8. Test delete (archive) project
    res = client.delete(f"/api/v1/projects/{proj_id}", headers=admin_headers)
    assert res.status_code == 204

    db.close()
