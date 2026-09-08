"""
FastAPI dependencies
--------------------
get_current_user   – validates Bearer JWT, returns User ORM object
require_admin      – further checks global role == ADMIN
get_project_member – validates the user belongs to a project
require_project_manager – project role must be OWNER or MANAGER
"""
 
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
 
from app.core.security import decode_token
from app.db.session import get_db
from app.models.models import GlobalRole, Project, ProjectMember, ProjectRole, User
 
bearer_scheme = HTTPBearer()
 
 
# ── Auth ──────────────────────────────────────────────────────────────────────
 
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_token(credentials.credentials, expected_type="access")
    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user
 
 
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != GlobalRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
 
 
# ── Project membership guards ─────────────────────────────────────────────────
 
def get_project_or_404(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if project is None or not project.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
 
 
def _get_membership(project_id: int, user: User, db: Session) -> ProjectMember:
    membership = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id, user_id=user.id)
        .first()
    )
    return membership
 
 
class ProjectAccessDep:
    """
    Reusable dependency factory.
    Usage:
        project_access = ProjectAccessDep()   # any member
        manager_access = ProjectAccessDep(min_role="manager")
    """
 
    ROLE_ORDER = {
        ProjectRole.MEMBER: 0,
        ProjectRole.MANAGER: 1,
        ProjectRole.OWNER: 2,
    }
 
    def __init__(self, min_role: ProjectRole = ProjectRole.MEMBER):
        self.min_role = min_role
 
    def __call__(
        self,
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> tuple[Project, ProjectMember]:
        # Global admins bypass all project-level restrictions
        if current_user.role == GlobalRole.ADMIN:
            project = get_project_or_404(project_id, db)
            # Synthesise a virtual owner membership so callers don't need None checks.
            # id=0 is used as a sentinel (no real row has id=0) so serialisation never
            # produces None for the id field.
            virtual = ProjectMember(
                id=0,
                project_id=project_id,
                user_id=current_user.id,
                role=ProjectRole.OWNER,
            )
            return project, virtual
 
        project = get_project_or_404(project_id, db)
        membership = _get_membership(project_id, current_user, db)
 
        if membership is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this project")
 
        if self.ROLE_ORDER[membership.role] < self.ROLE_ORDER[self.min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"At least '{self.min_role}' role required",
            )
 
        return project, membership
 
 
# Convenience pre-built instances
project_member_dep = ProjectAccessDep(min_role=ProjectRole.MEMBER)
project_manager_dep = ProjectAccessDep(min_role=ProjectRole.MANAGER)
project_owner_dep = ProjectAccessDep(min_role=ProjectRole.OWNER)
