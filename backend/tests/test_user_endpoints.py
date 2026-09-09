import sys
sys.path.insert(0, "backend")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app
from app.models.models import GlobalRole, User
from app.core.security import hash_password, create_access_token

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

def test_user_search_and_organization():
    db = TestingSessionLocal()
    admin = User(
        email="admin@acme.com",
        full_name="Alice Admin",
        organization_name="Acme",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.ADMIN,
        is_active=True,
    )
    emp1 = User(
        email="bob@acme.com",
        full_name="Bob Worker",
        organization_name="Acme",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.MEMBER,
        is_active=True,
    )
    emp2 = User(
        email="charlie@acme.com",
        full_name="Charlie Dev",
        organization_name="Acme",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.MEMBER,
        is_active=False,  # inactive
    )
    other_user = User(
        email="david@other.com",
        full_name="David Other",
        organization_name="OtherCorp",
        hashed_password=hash_password("Password123"),
        role=GlobalRole.MEMBER,
        is_active=True,
    )
    db.add_all([admin, emp1, emp2, other_user])
    db.commit()
    db.refresh(admin)
    db.refresh(emp1)

    admin_token = create_access_token(admin.id)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    emp1_token = create_access_token(emp1.id)
    emp1_headers = {"Authorization": f"Bearer {emp1_token}"}

    # 1. Search users as admin (should return emp1, not self, not inactive emp2, not other_user)
    r = client.get("/api/v1/users/search", headers=admin_headers)
    assert r.status_code == 200, r.text
    users = r.json()
    assert len(users) == 1
    assert users[0]["email"] == "bob@acme.com"

    # 2. Search users with query
    r = client.get("/api/v1/users/search?q=Bob", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get("/api/v1/users/search?q=NonExistent", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) == 0

    # 3. Organization users as admin
    r = client.get("/api/v1/users/organization", headers=admin_headers)
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1
    assert r.json()[0]["email"] == "bob@acme.com"

    # 4. Search users as regular employee (should find admin)
    r = client.get("/api/v1/users/search", headers=emp1_headers)
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1
    assert r.json()[0]["email"] == "admin@acme.com"

    # 5. Organization users as regular employee (should find admin)
    r = client.get("/api/v1/users/organization", headers=emp1_headers)
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1
    assert r.json()[0]["email"] == "admin@acme.com"
