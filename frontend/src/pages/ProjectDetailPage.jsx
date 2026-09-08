import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projects, tasks, users } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  Button, Modal, Input, Textarea, Select, ConfirmModal,
  StatusBadge, PriorityBadge, RoleBadge, Avatar, Empty, toast
} from '../components/ui';
import './ProjectDetail.css';

function formatDate(d) { return d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : null; }
function isOverdue(d, status) { return d && new Date(d) < new Date() && !['done','cancelled'].includes(status); }

const STATUSES = ['todo','in_progress','in_review','done','cancelled'];
const PRIORITIES = ['low','medium','high','critical'];
const ROLES = ['member','manager','owner'];

// ── Task Form ─────────────────────────────────────────────────────────────────
function TaskForm({ projectId, members, task, onSave, onClose, canManage, canAssign }) {
  const [form, setForm] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 'medium',
    status: task?.status || 'todo',
    due_date: task?.due_date ? task.due_date.slice(0,10) : '',
    assignee_id: task?.assignee?.id || '',
  });
  const [saving, setSaving] = useState(false);
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        assignee_id: canAssign && form.assignee_id ? Number(form.assignee_id) : null,
        due_date: form.due_date ? `${form.due_date}T00:00:00Z` : null,
      };
      if (!task) {
        await tasks.create(projectId, canAssign ? payload : { ...payload, assignee_id: null });
        toast('Task created!');
      } else {
        const updates = canManage ? (canAssign ? payload : { ...payload, assignee_id: task?.assignee_id || null }) : { status: payload.status };
        await tasks.update(projectId, task.id, updates);
        toast('Task updated!');
      }
      onSave();
      onClose();
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {canManage && (
        <>
          <Input id="task-title" label="Title" value={form.title} onChange={set('title')} required placeholder="What needs to be done?" autoFocus={!task} />
          <Textarea id="task-desc" label="Description" value={form.description} onChange={set('description')} placeholder="Additional context..." />
        </>
      )}
      {(!task || canManage) && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          {canManage && (
            <>
              <Select id="priority" label="Priority" value={form.priority} onChange={set('priority')}>
                {PRIORITIES.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase()+p.slice(1)}</option>)}
              </Select>
              {canAssign && (
                <Select id="assignee" label="Assignee" value={form.assignee_id} onChange={set('assignee_id')}>
                  <option value="">Unassigned</option>
                  {members.map(m => <option key={m.user.id} value={m.user.id}>{m.user.full_name}</option>)}
                </Select>
              )}
              <Input id="due-date" label="Due date" type="date" value={form.due_date} onChange={set('due_date')} />
            </>
          )}
          <Select id="status" label="Status" value={form.status} onChange={set('status')}>
            {STATUSES.map(s => <option key={s} value={s}>{s.replace('_',' ')}</option>)}
          </Select>
        </div>
      )}
      <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 8 }}>
        <Button variant="ghost" onClick={onClose} type="button">Cancel</Button>
        <Button type="submit" loading={saving}>{task ? 'Save changes' : 'Create Task'}</Button>
      </div>
    </form>
  );
}

// ── Add Member Form ───────────────────────────────────────────────────────────
function AddMemberForm({ projectId, existingMembers, onSave, onClose }) {
  const [form, setForm] = useState({ user_id: '', role: 'member' });
  const [employees, setEmployees] = useState([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    users.organization()
      .then(data => {
        const existingIds = new Set(existingMembers.map(m => m.user?.id));
        setEmployees(data.filter(employee => !existingIds.has(employee.id)));
      })
      .catch(e => toast(e.message, 'error'));
  }, [existingMembers]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.user_id) { toast('Select an employee', 'error'); return; }
    setSaving(true);
    try {
      await projects.addMember(projectId, { user_id: Number(form.user_id), role: form.role });
      toast('Member added!');
      onSave();
      onClose();
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <Select id="uid" label="Employee" value={form.user_id}
        onChange={e => setForm(f => ({ ...f, user_id: e.target.value }))} required>
        <option value="">Select an employee</option>
        {employees.map(employee => (
          <option key={employee.id} value={employee.id}>{employee.full_name} — {employee.email}</option>
        ))}
      </Select>
      <Select id="role" label="Role" value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}>
        {ROLES.map(r => <option key={r} value={r}>{r.charAt(0).toUpperCase()+r.slice(1)}</option>)}
      </Select>
      <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
        <Button variant="ghost" onClick={onClose} type="button">Cancel</Button>
        <Button type="submit" loading={saving}>Add Member</Button>
      </div>
    </form>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function ProjectDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [memberList, setMemberList] = useState([]);
  const [taskList, setTaskList] = useState([]);
  const [tab, setTab] = useState('tasks');
  const [loading, setLoading] = useState(true);
  const [taskModal, setTaskModal] = useState(null); // null | 'new' | task-obj
  const [addMember, setAddMember] = useState(false);
  const [deleteTask, setDeleteTask] = useState(null);
  const [removeMember, setRemoveMember] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');

  const myMembership = memberList.find(m => m.user?.id === user?.id);
  const canManage = user?.role === 'admin' || ['owner','manager'].includes(myMembership?.role);
  const canAssign = user?.role === 'admin';
  const isOwner = user?.role === 'admin' || myMembership?.role === 'owner';

  const load = useCallback(async () => {
    try {
      const [proj, members, tlist] = await Promise.all([
        projects.get(id),
        projects.listMembers(id),
        tasks.list(id),
      ]);
      setProject(proj);
      setMemberList(members);
      setTaskList(tlist);
    } catch (e) {
      toast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const reloadTasks = () => tasks.list(id, statusFilter ? { status: statusFilter } : {}).then(setTaskList);
  const reloadMembers = () => projects.listMembers(id).then(setMemberList);

  const handleDeleteTask = async (taskId) => {
    try { await tasks.delete(id, taskId); toast('Task deleted'); reloadTasks(); }
    catch (e) { toast(e.message, 'error'); }
  };

  const handleRemoveMember = async (uid) => {
    try { await projects.removeMember(id, uid); toast('Member removed'); reloadMembers(); }
    catch (e) { toast(e.message, 'error'); }
  };

  useEffect(() => { if (!loading) reloadTasks(); }, [statusFilter]);

  if (loading) return <div className="page"><div className="skeleton" style={{ height: 40, width: 220, marginBottom: 24 }} /></div>;
  if (!project) return <div className="page"><div style={{ color: 'var(--text-2)' }}>Project not found.</div></div>;

  const filteredTasks = statusFilter ? taskList.filter(t => t.status === statusFilter) : taskList;

  return (
    <div className="page animate-fade">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ color: 'var(--text-2)', fontSize: 13, marginBottom: 4, cursor: 'pointer' }} onClick={() => navigate('/projects')}>← Projects</div>
          <div className="page-title">{project.name}</div>
          {project.description && <div className="page-subtitle">{project.description}</div>}
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          {tab === 'tasks' && canManage && (
            <Button onClick={() => setTaskModal('new')}>+ New Task</Button>
          )}
          {tab === 'members' && canAssign && (
            <Button onClick={() => setAddMember(true)}>+ Add Member</Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="pd-tabs">
        <button className={`pd-tab ${tab === 'tasks' ? 'active' : ''}`} onClick={() => setTab('tasks')}>
          Tasks <span className="pd-tab-count">{taskList.length}</span>
        </button>
        <button className={`pd-tab ${tab === 'members' ? 'active' : ''}`} onClick={() => setTab('members')}>
          Members <span className="pd-tab-count">{memberList.length}</span>
        </button>
      </div>

      {/* Tasks tab */}
      {tab === 'tasks' && (
        <>
          <div className="pd-filters">
            <select className="field-input field-select" style={{ width: 'auto' }}
              value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
              <option value="">All statuses</option>
              {STATUSES.map(s => <option key={s} value={s}>{s.replace('_',' ')}</option>)}
            </select>
          </div>

          {!filteredTasks.length ? (
            <Empty icon="📋" title="No tasks" desc={statusFilter ? 'No tasks with this status.' : 'Create your first task.'}
              action={canManage && <Button onClick={() => setTaskModal('new')}>Create task</Button>} />
          ) : (
            <div className="task-table">
              <div className="task-table-header">
                <span>Title</span>
                <span>Status</span>
                <span>Priority</span>
                <span>Assignee</span>
                <span>Due</span>
                <span></span>
              </div>
              {filteredTasks.map(task => (
                <div key={task.id} className="task-row" onClick={() => setTaskModal(task)}>
                  <div className="task-title-cell">
                    <span className={`task-title ${isOverdue(task.due_date, task.status) ? 'overdue' : ''}`}>{task.title}</span>
                    {task.description && <span className="task-desc-preview">{task.description}</span>}
                  </div>
                  <StatusBadge status={task.status} />
                  <PriorityBadge priority={task.priority} />
                  <div className="task-assignee">
                    {task.assignee ? <><Avatar name={task.assignee.full_name} size={22} /><span>{task.assignee.full_name.split(' ')[0]}</span></> : <span style={{ color: 'var(--text-3)' }}>—</span>}
                  </div>
                  <span className={`task-due ${isOverdue(task.due_date, task.status) ? 'overdue' : ''}`}>{formatDate(task.due_date) || '—'}</span>
                  {canManage && (
                    <button className="task-delete" onClick={e => { e.stopPropagation(); setDeleteTask(task.id); }}>✕</button>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Members tab */}
      {tab === 'members' && (
        <div className="members-list">
          {memberList.map(m => (
            <div key={m.id} className="member-row">
              <Avatar name={m.user?.full_name} size={36} />
              <div className="member-info">
                <div className="member-name">{m.user?.full_name}</div>
                <div className="member-email">{m.user?.email}</div>
              </div>
              <RoleBadge role={m.role} />
              {isOwner && m.user?.id !== user?.id && (
                <button className="task-delete" onClick={() => setRemoveMember(m.user?.id)} title="Remove member">✕</button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      <Modal open={taskModal !== null} onClose={() => setTaskModal(null)}
        title={taskModal === 'new' ? 'New Task' : 'Edit Task'} width={540}>
        {taskModal !== null && (
          <TaskForm
            projectId={id}
            members={memberList}
            task={taskModal === 'new' ? null : taskModal}
            onSave={reloadTasks}
            onClose={() => setTaskModal(null)}
            canManage={canManage}
            canAssign={canAssign}
          />
        )}
      </Modal>

      <Modal open={addMember} onClose={() => setAddMember(false)} title="Add Member">
        <AddMemberForm projectId={id} existingMembers={memberList} onSave={reloadMembers} onClose={() => setAddMember(false)} />
      </Modal>

      <ConfirmModal open={!!deleteTask} onClose={() => setDeleteTask(null)}
        onConfirm={() => handleDeleteTask(deleteTask)}
        title="Delete Task" message="This task will be permanently deleted." danger />

      <ConfirmModal open={!!removeMember} onClose={() => setRemoveMember(null)}
        onConfirm={() => handleRemoveMember(removeMember)}
        title="Remove Member" message="Remove this member from the project?" danger />
    </div>
  );
}
