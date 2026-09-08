"""
/projects/{project_id}/tasks  – task management inside a project.
 
Role matrix
-----------
List / Get tasks  : project member (any role)
Create task       : MANAGER+ or admin (only admin may assign)
Update task       : assignee can update status only; MANAGER+ can update all fields except assignment (admin only)
Delete task       : MANAGER+ or admin
"""
 
from datetime import datetime, timezone
from typing import Optional
 
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
 
from app.api.v1.deps import (
    get_current_user,
    project_manager_dep,
    project_member_dep,
)
from app.db.session import get_db
from app.models.models import GlobalRole, ProjectMember, ProjectRole, Task, TaskStatus, User
from app.schemas.schemas import TaskCreate, TaskResponse, TaskUpdate
 
router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Tasks"],
)
 
 
def _load_task(task_id: int, project_id: int, db: Session) -> Task:
    task = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(Task.id == task_id, Task.project_id == project_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
 
 
# ── Endpoints ─────────────────────────────────────────────────────────────────
 
@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    assignee_id: Optional[int] = Query(None),
    overdue_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    """List tasks for a project with optional filters."""
    project, _ = access
    q = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(Task.project_id == project.id)
    )
    if status_filter:
        q = q.filter(Task.status == status_filter)
    if assignee_id:
        q = q.filter(Task.assignee_id == assignee_id)
    if overdue_only:
        now = datetime.now(timezone.utc)
        q = q.filter(Task.due_date < now, Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED]))
 
    return q.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
 
 
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    """Create a task (admin only)."""
    project, _ = access
    if current_user.role != GlobalRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can assign/create tasks")
 
    if payload.assignee_id and current_user.role != GlobalRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can assign tasks")

    # Validate assignee belongs to this project
    if payload.assignee_id:
        assignee_membership = (
            db.query(ProjectMember)
            .filter_by(project_id=project.id, user_id=payload.assignee_id)
            .first()
        )
        if not assignee_membership:
            raise HTTPException(status_code=400, detail="Assignee must be a project member")
 
    task = Task(
        **payload.model_dump(),
        project_id=project.id,
        creator_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _load_task(task.id, project.id, db)
 
 
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    project, _ = access
    return _load_task(task_id, project.id, db)
 
 
@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    """
    Update a task.
    - MANAGER+ / admin : can update all fields
    - Regular MEMBER   : can only update status, and only on tasks assigned to them
    """
    project, membership = access
    task = _load_task(task_id, project.id, db)
 
    is_privileged = current_user.role == GlobalRole.ADMIN
 
    if not is_privileged:
        # Non-privileged users may only touch their own assigned tasks
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update tasks assigned to you")
 
        updates = payload.model_dump(exclude_none=True)
        disallowed = set(updates.keys()) - {"status"}
        if disallowed:
            raise HTTPException(
                status_code=403,
                detail=f"Members can only update 'status'. Disallowed fields: {disallowed}",
            )
    else:
        updates = payload.model_dump(exclude_none=True)
 
    if "assignee_id" in updates and updates["assignee_id"] != task.assignee_id and current_user.role != GlobalRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can assign tasks")

    # Validate new assignee is a project member
    if "assignee_id" in updates and updates["assignee_id"] is not None:
        assignee_membership = (
            db.query(ProjectMember)
            .filter_by(project_id=project.id, user_id=updates["assignee_id"])
            .first()
        )
        if not assignee_membership:
            raise HTTPException(status_code=400, detail="New assignee must be a project member")
 
    for field, value in updates.items():
        setattr(task, field, value)
 
    db.commit()
    return _load_task(task.id, project.id, db)
 
 
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    access=Depends(project_member_dep),
    db: Session = Depends(get_db),
):
    """Delete a task (admin only)."""
    project, _ = access
    if current_user.role != GlobalRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can delete tasks")
    task = _load_task(task_id, project.id, db)
    db.delete(task)
    db.commit()
 




