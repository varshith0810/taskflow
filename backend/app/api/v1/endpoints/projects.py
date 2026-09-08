"""
/projects  – project CRUD and member management.
 
Role matrix
-----------
List projects    : any authenticated user (sees own projects; admin sees all)
Create project   : admin only (can add employees from the same organization)
Get project      : project member OR admin
Update project   : OWNER / MANAGER / admin
Delete project   : OWNER / admin
Add member       : OWNER / MANAGER / admin
Update member    : OWNER / admin
Remove member    : OWNER / admin  (or the member themselves — self-leave)
"""
 
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
 
from app.api.v1.deps import (
    get_current_user,
    project_manager_dep,
    project_member_dep,
    project_owner_dep,
    require_admin,
)
from app.db.session import get_db
from app.models.models import GlobalRole, Project, ProjectMember, ProjectRole, User
from app.schemas.schemas import (
    AddMemberRequest,
    MemberInProject,
    ProjectCreate,
    ProjectDetail,
    ProjectResponse,
    ProjectUpdate,
    UpdateMemberRole,
)
 
router = APIRouter(prefix="/projects", tags=["Projects"])
 
 
# ── CRUD ──────────────────────────────────────────────────────────────────────
 
@router.get("", response_model=list[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List projects the caller belongs to (admin sees all)."""
    q = db.query(Project).filter(Project.is_active == True)
    if current_user.role != GlobalRole.ADMIN:
        q = q.join(ProjectMember).filter(ProjectMember.user_id == current_user.id)
    return q.offset(skip).limit(limit).all()
 
 
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a project. Admin can select employees from their organization."""
    data = payload.model_dump(exclude={"member_ids"})
    selected_member_ids = set(payload.member_ids)
    selected_member_ids.discard(current_user.id)

    if selected_member_ids:
        selected_members = (
            db.query(User)
            .filter(
                User.id.in_(selected_member_ids),
                User.is_active == True,
                User.organization_name == current_user.organization_name,
            )
            .all()
        )
        if len(selected_members) != len(selected_member_ids):
            raise HTTPException(
                status_code=400,
                detail="Selected employees must be active users in your organization",
            )
    else:
        selected_members = []

    project = Project(**data)

    project = Project(**data)
    """Create a project (admin only). The creator is automatically added as OWNER."""
    project = Project(**payload.model_dump())

    db.add(project)
    db.flush()  # get project.id before commit
    membership = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role=ProjectRole.OWNER,
    )
    db.add(membership)

    for member in selected_members:
        db.add(ProjectMember(
            project_id=project.id,
            user_id=member.id,
            role=ProjectRole.MEMBER,
        ))

    db.commit()
    db.refresh(project)
    return project
 
 
@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    """Get project details including members and task count."""
    project, _ = access
    project_with_members = (
        db.query(Project)
        .options(joinedload(Project.members).joinedload(ProjectMember.user))
        .filter(Project.id == project.id)
        .one()
    )
    task_count = len(project_with_members.tasks)
    detail = ProjectDetail.model_validate(project_with_members)
    detail.task_count = task_count
    return detail
 
 
@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    payload: ProjectUpdate,
    access=Depends(project_manager_dep),
    db: Session = Depends(get_db),
):
    """Update project metadata (MANAGER+ or admin)."""
    project, _ = access
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project
 
 
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    access=Depends(project_owner_dep),
    db: Session = Depends(get_db),
):
    """Soft-delete (archive) a project (OWNER or admin)."""
    project, _ = access
    project.is_active = False
    db.commit()
 
 
# ── Member management ─────────────────────────────────────────────────────────
 
@router.get("/{project_id}/members", response_model=list[MemberInProject])
def list_members(
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    project, _ = access
    return (
        db.query(ProjectMember)
        .options(joinedload(ProjectMember.user))
        .filter_by(project_id=project.id)
        .all()
    )
 
 
@router.post("/{project_id}/members", response_model=MemberInProject, status_code=status.HTTP_201_CREATED)
def add_member(
    payload: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    access=Depends(project_manager_dep),
    db: Session = Depends(get_db),
):
    """Add a user to the project (MANAGER+ or admin)."""
    project, _ = access

    target_user = db.get(User, payload.user_id)
    if not target_user or not target_user.is_active:
        raise HTTPException(status_code=404, detail="Target user not found")
 
    if current_user and target_user.organization_name != current_user.organization_name:
        raise HTTPException(status_code=400, detail="Target user must be in your organization")

    existing = db.query(ProjectMember).filter_by(project_id=project.id, user_id=payload.user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member")
 
    membership = ProjectMember(project_id=project.id, user_id=payload.user_id, role=payload.role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership
 
 
@router.patch("/{project_id}/members/{user_id}", response_model=MemberInProject)
def update_member_role(
    user_id: int,
    payload: UpdateMemberRole,
    access=Depends(project_owner_dep),
    db: Session = Depends(get_db),
):
    """Change a member's project role (OWNER or admin)."""
    project, _ = access
    membership = db.query(ProjectMember).filter_by(project_id=project.id, user_id=user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    membership.role = payload.role
    db.commit()
    db.refresh(membership)
    return membership
 
 
@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    user_id: int,
    current_user: User = Depends(get_current_user),
    # Use project_member_dep (not owner_dep) so regular members can reach this
    # endpoint and self-leave. Elevation to owner is checked manually below.
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    """Remove a member from the project.
 
    Allowed when:
      - caller is the OWNER or a global ADMIN, OR
      - caller is removing themselves (self-leave)
    """
    project, caller_membership = access
 
    is_owner_or_admin = (
        caller_membership.role == ProjectRole.OWNER
        or current_user.role == GlobalRole.ADMIN
    )
    is_self_leave = current_user.id == user_id
 
    if not is_owner_or_admin and not is_self_leave:
        raise HTTPException(status_code=403, detail="Not allowed to remove other members")
 
    membership = db.query(ProjectMember).filter_by(project_id=project.id, user_id=user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
 
    if membership.role == ProjectRole.OWNER:
        owners = db.query(ProjectMember).filter_by(project_id=project.id, role=ProjectRole.OWNER).count()
        if owners <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last owner")
 
    db.delete(membership)
    db.commit()
