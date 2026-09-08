import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Avatar } from './ui';
import './Layout.css';

const NAV = [
  { path: '/dashboard', icon: '◈', label: 'Dashboard' },
  { path: '/projects', icon: '⬡', label: 'Projects' },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className={`layout ${collapsed ? 'layout-collapsed' : ''}`}>
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="sidebar-brand">
            <div className="brand-mark">T</div>
            {!collapsed && <span className="brand-name">TaskFlow</span>}
          </div>
          <button className="sidebar-toggle" onClick={() => setCollapsed(c => !c)}>
            {collapsed ? '›' : '‹'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {NAV.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname.startsWith(item.path) ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {!collapsed && <span className="nav-label">{item.label}</span>}
            </Link>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="user-row">
            <Avatar name={user?.full_name} size={32} />
            {!collapsed && (
              <div className="user-info">
                <div className="user-name">{user?.full_name}</div>
                <div className="user-role">{user?.role}</div>
              </div>
            )}
          </div>
          {!collapsed && (
            <button className="logout-btn" onClick={handleLogout}>Sign out</button>
          )}
        </div>
      </aside>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
