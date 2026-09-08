"""
SQLAlchemy ORM models for the Team Task Manager.

Tables
------
users            – accounts (Admin or regular Member)
projects         – top-level containers
project_members  – many-to-many: user ↔ project (with per-project role)
tasks            – belong to a project, optionally assigned to a user
"""

from __future__ import annotations
import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
# ── Enums ─────────────────────────────────────────────────────────────────────
class GlobalRole(str, enum.Enum):
    """Platform-wide role stored on the User row."""
    ADMIN = "admin"    # can manage all projects & users
    MEMBER = "member"  # regular user


class ProjectRole(str, enum.Enum):
    """Per-project role stored on the ProjectMember row."""
    OWNER = "owner"     # created the project; full control
    MANAGER = "manager" # can create / delete tasks, add members
    MEMBER = "member"   # can update task status only


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Helper ────────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Models ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    organization_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[GlobalRole] = mapped_column(
        Enum(GlobalRole), default=GlobalRole.MEMBER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    # relationships
    memberships: Mapped[list[ProjectMember]] = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    assigned_tasks: Mapped[list[Task]] = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    created_tasks: Mapped[list[Task]] = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    # relationships
    members: Mapped[list[ProjectMember]] = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list[Task]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_user"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole), default=ProjectRole.MEMBER, nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # relationships
    project: Mapped[Project] = relationship("Project", back_populates="members")
    user: Mapped[User] = relationship("User", back_populates="memberships")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.TODO, nullable=False, index=True
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    # relationships
    project: Mapped[Project] = relationship("Project", back_populates="tasks")
    creator: Mapped[User | None] = relationship("User", back_populates="created_tasks", foreign_keys=[creator_id])
    assignee: Mapped[User | None] = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
