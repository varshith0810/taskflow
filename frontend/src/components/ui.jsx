import { useState } from 'react';

// ── Button ────────────────────────────────────────────────────────────────────
export function Button({ children, variant = 'primary', size = 'md', loading, disabled, onClick, type = 'button', className = '', ...props }) {
  const base = 'btn';
  return (
    <button
      type={type}
      className={`btn btn-${variant} btn-${size} ${loading ? 'btn-loading' : ''} ${className}`}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && <span className="spinner" />}
      {children}
    </button>
  );
}

// ── Input ────────────────────────────────────────────────────────────────────
export function Input({ label, error, id, className = '', ...props }) {
  return (
    <div className="field">
      {label && <label htmlFor={id} className="field-label">{label}</label>}
      <input id={id} className={`field-input ${error ? 'field-error' : ''} ${className}`} {...props} />
      {error && <span className="field-hint error">{error}</span>}
    </div>
  );
}

// ── Select ────────────────────────────────────────────────────────────────────
export function Select({ label, error, id, children, className = '', ...props }) {
  return (
    <div className="field">
      {label && <label htmlFor={id} className="field-label">{label}</label>}
      <select id={id} className={`field-input field-select ${error ? 'field-error' : ''} ${className}`} {...props}>
        {children}
      </select>
      {error && <span className="field-hint error">{error}</span>}
    </div>
  );
}

// ── Textarea ────────────────────────────────────────────────────────────────
export function Textarea({ label, error, id, className = '', ...props }) {
  return (
    <div className="field">
      {label && <label htmlFor={id} className="field-label">{label}</label>}
      <textarea id={id} className={`field-input ${error ? 'field-error' : ''} ${className}`} rows={3} {...props} />
      {error && <span className="field-hint error">{error}</span>}
    </div>
  );
}

// ── Badge ────────────────────────────────────────────────────────────────────
const STATUS_MAP = {
  todo: { label: 'Todo', color: 'badge-neutral' },
  in_progress: { label: 'In Progress', color: 'badge-blue' },
  in_review: { label: 'In Review', color: 'badge-purple' },
  done: { label: 'Done', color: 'badge-green' },
  cancelled: { label: 'Cancelled', color: 'badge-red' },
};
const PRIORITY_MAP = {
  low: { label: 'Low', color: 'badge-neutral' },
  medium: { label: 'Medium', color: 'badge-blue' },
  high: { label: 'High', color: 'badge-amber' },
  critical: { label: 'Critical', color: 'badge-red' },
};
const ROLE_MAP = {
  owner: { label: 'Owner', color: 'badge-amber' },
  manager: { label: 'Manager', color: 'badge-blue' },
  member: { label: 'Member', color: 'badge-neutral' },
};

export function StatusBadge({ status }) {
  const { label, color } = STATUS_MAP[status] || { label: status, color: 'badge-neutral' };
  return <span className={`badge ${color}`}>{label}</span>;
}
export function PriorityBadge({ priority }) {
  const { label, color } = PRIORITY_MAP[priority] || { label: priority, color: 'badge-neutral' };
  return <span className={`badge ${color}`}>{label}</span>;
}
export function RoleBadge({ role }) {
  const { label, color } = ROLE_MAP[role] || { label: role, color: 'badge-neutral' };
  return <span className={`badge ${color}`}>{label}</span>;
}

// ── Modal ────────────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children, width = 480 }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: width }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

// ── Toast ────────────────────────────────────────────────────────────────────
let _toastFn = null;
export function setToastFn(fn) { _toastFn = fn; }
export function toast(msg, type = 'success') { _toastFn?.(msg, type); }

export function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    setToastFn((msg, type) => {
      const id = Date.now();
      setToasts(t => [...t, { id, msg, type }]);
      setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3500);
    });
  }, []);

  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>{t.msg}</div>
      ))}
    </div>
  );
}

// ── Avatar ────────────────────────────────────────────────────────────────────
export function Avatar({ name, size = 32 }) {
  const initials = (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
  const hue = (name || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0) % 360;
  return (
    <div className="avatar" style={{ width: size, height: size, fontSize: size * 0.38, background: `hsl(${hue},55%,35%)` }}>
      {initials}
    </div>
  );
}

// ── Empty state ────────────────────────────────────────────────────────────────
export function Empty({ icon, title, desc, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <div className="empty-title">{title}</div>
      {desc && <div className="empty-desc">{desc}</div>}
      {action}
    </div>
  );
}

// ── Confirm dialog ────────────────────────────────────────────────────────────
export function ConfirmModal({ open, onClose, onConfirm, title, message, danger }) {
  return (
    <Modal open={open} onClose={onClose} title={title} width={380}>
      <p style={{ color: 'var(--text-1)', marginBottom: 24 }}>{message}</p>
      <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button variant={danger ? 'danger' : 'primary'} onClick={() => { onConfirm(); onClose(); }}>Confirm</Button>
      </div>
    </Modal>
  );
}

// ── useEffect import fix ───────────────────────────────────────────────────────
import { useEffect } from 'react';
