from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.models import GlobalRole, ProjectRole, TaskStatus, TaskPriority
import re
class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str
    organization_name: str
    password: str
    role: GlobalRole = GlobalRole.MEMBER

    @field_validator("organization_name")
    @classmethod
    def organization_required(cls, v):
        value = v.strip()
        if not value:
            raise ValueError("Organization name is required")
        return value

    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if not re.match(r'^(?=.*[A-Z])(?=.*\d).{8,}$', v):
            raise ValueError("Password must be 8+ chars with at least one uppercase and one digit")
        return v
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class RefreshRequest(BaseModel):
    refresh_token: str
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
class UserPublic(BaseModel):
    id: int
    email: str
    full_name: str
    organization_name: str
    role: GlobalRole
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    member_ids: List[int] = Field(default_factory=list)
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
class MemberInProject(BaseModel):
    id: int
    user_id: int
    project_id: int
    role: ProjectRole
    joined_at: datetime
    user: Optional[UserPublic] = None
    model_config = {"from_attributes": True}
class ProjectDetail(ProjectResponse):
    members: List[MemberInProject] = []
    task_count: int = 0
class AddMemberRequest(BaseModel):
    user_id: int
    role: ProjectRole = ProjectRole.MEMBER
class UpdateMemberRole(BaseModel):
    role: ProjectRole
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    project_id: int
    creator_id: Optional[int]
    assignee_id: Optional[int]
    creator: Optional[UserPublic] = None
    assignee: Optional[UserPublic] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
class TaskStatusCount(BaseModel):
    status: TaskStatus
    count: int
class MemberTaskCount(BaseModel):
    """Task load per member for manager dashboard insights."""
    user_id: int
    full_name: str
    task_count: int
class DashboardResponse(BaseModel):
    total_projects: int
    total_tasks: int
    overdue_tasks: int
    tasks_by_status: List[TaskStatusCount]
    my_assigned_tasks: List[TaskResponse]
    member_task_counts: List[MemberTaskCount]
    managed_tasks: List[TaskResponse]

