from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import UserPublic

router = APIRouter(prefix="", tags=["Users"])


@router.get("/users/search", response_model=list[UserPublic])
def search_users(
    q: str = Query("", description="Search by email or name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search active users in the caller's organization."""
    if not current_user.organization_name:
        return []
    query = db.query(User).filter(
        User.is_active.is_(True),
        User.id != current_user.id,
        User.organization_name == current_user.organization_name,
    )
    if q and q.strip():
        term = q.strip()
        query = query.filter(User.email.ilike(f"%{term}%") | User.full_name.ilike(f"%{term}%"))
    return query.order_by(User.full_name.asc()).limit(50).all()


@router.get("/users/organization", response_model=list[UserPublic])
def organization_users(
    q: str = Query("", description="Search by email or name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List employees from the caller's organization for project selection."""
    if not current_user.organization_name:
        return []
    query = db.query(User).filter(
        User.is_active.is_(True),
        User.id != current_user.id,
        User.organization_name == current_user.organization_name,
    )
    if q and q.strip():
        term = q.strip()
        query = query.filter(User.email.ilike(f"%{term}%") | User.full_name.ilike(f"%{term}%"))
    return query.order_by(User.full_name.asc()).limit(200).all()
