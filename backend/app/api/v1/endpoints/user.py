from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, require_admin
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
    query = db.query(User).filter(
        User.is_active == True,
        User.id != current_user.id,
        User.organization_name == current_user.organization_name,
    )
    if q:
        query = query.filter(User.email.ilike(f"%{q}%") | User.full_name.ilike(f"%{q}%"))
    return query.order_by(User.full_name.asc()).limit(50).all()


@router.get("/users/organization", response_model=list[UserPublic])
def organization_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List employees from the admin's organization for project selection."""
    return (
        db.query(User)
        .filter(
            User.is_active == True,
            User.id != current_user.id,
            User.organization_name == current_user.organization_name,


            (User.email.ilike(f"%{q}%") | User.full_name.ilike(f"%{q}%")),


        )
        .order_by(User.full_name.asc())
        .limit(200)
        .all()
    )
