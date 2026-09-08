import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { projects, users } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Button, Modal, Input, Textarea, ConfirmModal, Empty, toast } from '../components/ui';
import './Projects.css';

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function ProjectsPage() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', member_ids: [] });
  const [employees, setEmployees] = useState([]);
  const [saving, setSaving] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const load = () => {
    setLoading(true);
    projects.list()
      .then(setList)
      .catch(e => toast(e.message, 'error'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  useEffect(() => {
    if (creating && isAdmin) {
      users.organization()
        .then(setEmployees)
        .catch(e => toast(e.message, 'error'));
    }
  }, [creating, isAdmin]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      const p = await projects.create(form);
      toast('Project created!');
      setCreating(false);
      setForm({ name: '', description: '', member_ids: [] });
      navigate(`/projects/${p.id}`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await projects.delete(id);
      toast('Project archived');
      load();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div className="page animate-fade">
      <div className="page-header">
        <div>
          <div className="page-title">Projects</div>
          <div className="page-subtitle">{list.length} active project{list.length !== 1 ? 's' : ''}</div>
        </div>
        {isAdmin && <Button onClick={() => setCreating(true)}>+ New Project</Button>}
      </div>

      {loading ? (
        <div className="projects-grid">
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: 120, borderRadius: 12 }} />)}
        </div>
      ) : !list.length ? (
        <Empty
          icon="⬡"
          title="No projects yet"
          desc="Create your first project to start organizing work."
          action={isAdmin ? <Button onClick={() => setCreating(true)}>Create project</Button> : null}
        />
      ) : (
        <div className="projects-grid">
          {list.map(p => (
            <div key={p.id} className="project-card" onClick={() => navigate(`/projects/${p.id}`)}>
              <div className="project-card-top">
                <div className="project-card-name">{p.name}</div>
                {isAdmin && <button
                  className="project-delete-btn"
                  onClick={e => { e.stopPropagation(); setDeleteId(p.id); }}
                  title="Archive project"
                >✕</button>}
              </div>
              {p.description && <div className="project-card-desc">{p.description}</div>}
              <div className="project-card-footer">
                <span className="project-date">Created {formatDate(p.created_at)}</span>
                <span className="project-arrow">→</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      <Modal open={creating} onClose={() => setCreating(false)} title="New Project">
        <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Input
            id="proj-name" label="Project name"
            value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            placeholder="My awesome project" required autoFocus
          />
          <Textarea
            id="proj-desc" label="Description (optional)"
            value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="What's this project about?"
          />
          <div className="project-employee-picker">
            <div>
              <div className="input-label">Employees in {user?.organization_name || 'your organization'}</div>
              <div className="project-employee-help">Select employees to add to this project when it is created.</div>
            </div>
            {!employees.length ? (
              <div className="project-employee-empty">No other employees found in your organization.</div>
            ) : employees.map(employee => (
              <label key={employee.id} className="project-employee-option">
                <input
                  type="checkbox"
                  checked={form.member_ids.includes(employee.id)}
                  onChange={e => setForm(f => ({
                    ...f,
                    member_ids: e.target.checked
                      ? [...f.member_ids, employee.id]
                      : f.member_ids.filter(id => id !== employee.id),
                  }))}
                />
                <span>
                  <strong>{employee.full_name}</strong>
                  <small>{employee.email}</small>
                </span>
              </label>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 8 }}>
            <Button variant="ghost" onClick={() => setCreating(false)} type="button">Cancel</Button>
            <Button type="submit" loading={saving}>Create Project</Button>
          </div>
        </form>
      </Modal>

      {/* Delete confirm */}
      <ConfirmModal
        open={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={() => handleDelete(deleteId)}
        title="Archive Project"
        message="This will archive the project and hide it from all members. Tasks will be preserved."
        danger
      />
    </div>
  );
}
