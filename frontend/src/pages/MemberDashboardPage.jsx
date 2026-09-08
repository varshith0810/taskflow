import { useEffect, useState } from 'react';
import { dashboard } from '../api/client';
import { StatusBadge, PriorityBadge, Empty } from '../components/ui';
import './Dashboard.css';

function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function MemberDashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    dashboard.get().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page"><div className="page-title">Loading…</div></div>;
  if (error) return <div className="page"><div className="error-msg">{error}</div></div>;

  return (
    <div className="page animate-fade">
      <div className="page-header">
        <div>
          <div className="page-title">Member Dashboard</div>
          <div className="page-subtitle">Your assigned work</div>
        </div>
      </div>
      <div className="card">
        <div className="card-title" style={{ marginBottom: 16 }}>My Assigned Tasks</div>
        {!data?.my_assigned_tasks?.length ? (
          <Empty icon="✓" title="All clear!" desc="No open tasks assigned to you." />
        ) : (
          <div className="my-tasks-list">
            {data.my_assigned_tasks.map(task => (
              <div key={task.id} className="my-task-item">
                <div className="my-task-main">
                  <div className="my-task-title">{task.title}</div>
                  <div className="my-task-meta">
                    <StatusBadge status={task.status} />
                    <PriorityBadge priority={task.priority} />
                  </div>
                </div>
                <div className="my-task-due">{formatDate(task.due_date)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
