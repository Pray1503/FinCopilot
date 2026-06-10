import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/dashboard', icon: 'dashboard', label: 'Dashboard' },
  { to: '/chat',      icon: 'smart_toy', label: 'Copilot Chat' },
  { to: '/boardroom', icon: 'groups',    label: 'Boardroom' },
  { to: '/cashflow',  icon: 'monitoring', label: 'Cash Flow' },
  { to: '/simulator', icon: 'calculate', label: 'Simulator' },
  { to: '/spending',  icon: 'analytics', label: 'Spending' },
  { to: '/bills',     icon: 'receipt_long', label: 'Bill Scanner' },
];

export default function Sidebar() {
  return (
    <aside className="layout-sidebar">
      {/* Brand */}
      <NavLink to="/" style={{ textDecoration: 'none' }}>
        <div style={{ padding: '0 20px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: 32, height: 32, borderRadius: 'var(--radius-sm)',
              background: 'var(--accent-violet)', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: 18, color: '#fff' }}>rocket_launch</span>
            </div>
            <div>
              <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>FinPilot</div>
              <div style={{ fontSize: 10, fontFamily: "'Geist', monospace", color: 'var(--text-muted)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                AI Financial OS
              </div>
            </div>
          </div>
        </div>
      </NavLink>

      {/* Navigation */}
      <nav style={{ flex: 1, paddingTop: 12 }}>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            style={{ textDecoration: 'none' }}
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: 'var(--accent-emerald)',
          }} className="animate-pulse" />
          <span className="text-label-caps" style={{ color: 'var(--accent-emerald)', fontSize: 10 }}>
            System Online
          </span>
        </div>
      </div>
    </aside>
  );
}
