import { useEffect, useState } from 'react';
import { dashboard } from '../api/client';
import { StatusBadge, PriorityBadge, Empty } from '../components/ui';
import './Dashboard.css';

function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function isOverdue(d) {
  return d && new Date(d) < new Date();
}

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    dashboard
      .get()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="page">
        <div className="page-header"><div className="skeleton" style={{ width: 180, height: 30 }} /></div>
        <div className="dash-stats">
          {[1, 2, 3, 4].map((i) => <div key={i} className="skeleton" style={{ height: 90, borderRadius: 12 }} />)}
        </div>
      </div>
    );
  }

  if (error) return <div className="page"><div className="error-msg">{error}</div></div>;

  const statusOrder = ['todo', 'in_progress', 'in_review', 'done', 'cancelled'];
  const byStatus = Object.fromEntries((data?.tasks_by_status || []).map((s) => [s.status, s.count]));

  return (
    <div className="page animate-fade">
      <div className="page-header">
        <div>
          <div className="page-title">Dashboard</div>
          <div className="page-subtitle">Manager workspace at a glance</div>
        </div>
      </div>

      <div className="dash-stats">
        <div className="stat-card">
          <div className="stat-label">Total Projects</div>
          <div className="stat-value amber">{data?.total_projects ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Tasks Allocated by You</div>
          <div className="stat-value">{data?.total_tasks ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Overdue</div>
          <div className={`stat-value ${(data?.overdue_tasks ?? 0) > 0 ? 'red' : 'green'}`}>{data?.overdue_tasks ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">My Open Tasks</div>
          <div className="stat-value">{data?.my_assigned_tasks?.length ?? 0}</div>
        </div>
      </div>

      <div className="dash-grid">
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Tasks by Status</div>
          <div className="status-bars">
            {statusOrder.map((s) => (
              <div key={s} className="status-bar-row">
                <StatusBadge status={s} />
                <div className="status-bar-track">
                  <div
                    className={`status-bar-fill status-fill-${s}`}
                    style={{ width: data?.total_tasks ? `${((byStatus[s] || 0) / data.total_tasks) * 100}%` : '0%' }}
                  />
                </div>
                <span className="status-count">{byStatus[s] || 0}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>My Assigned Tasks</div>
          {!data?.my_assigned_tasks?.length ? (
            <Empty icon="✓" title="All clear!" desc="No open tasks assigned to you." />
          ) : (
            <div className="my-tasks-list">
              {data.my_assigned_tasks.map((task) => (
                <div key={task.id} className="my-task-item">
                  <div className="my-task-main">
                    <div className="my-task-title">{task.title}</div>
                    <div className="my-task-meta">
                      <StatusBadge status={task.status} />
                      <PriorityBadge priority={task.priority} />
                    </div>
                  </div>
                  {task.due_date && (
                    <div className={`my-task-due ${isOverdue(task.due_date) ? 'overdue' : ''}`}>
                      {formatDate(task.due_date)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Member Task Load</div>
          {!data?.member_task_counts?.length ? (
            <Empty icon="👥" title="No assigned tasks" desc="Task load by member will appear here." />
          ) : (
            <div className="my-tasks-list">
              {data.member_task_counts.map((member) => (
                <div key={member.user_id} className="my-task-item">
                  <div className="my-task-title">{member.full_name}</div>
                  <div className="my-task-due">{member.task_count} tasks</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Managed Tasks & Progress</div>
          {!data?.managed_tasks?.length ? (
            <Empty icon="📌" title="No managed tasks" desc="Tasks from your managed projects will appear here." />
          ) : (
            <div className="my-tasks-list">
              {data.managed_tasks.map((task) => (
                <div key={task.id} className="my-task-item">
                  <div className="my-task-main">
                    <div className="my-task-title">{task.title}</div>
                    <div className="my-task-meta">
                      <StatusBadge status={task.status} />
                      <PriorityBadge priority={task.priority} />
                    </div>
                  </div>
                  <div className="my-task-due">{task.assignee?.full_name || 'Unassigned'}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
