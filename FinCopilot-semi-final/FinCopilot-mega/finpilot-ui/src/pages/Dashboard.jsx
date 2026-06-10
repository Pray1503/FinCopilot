import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import MetricCard from '../components/MetricCard';
import ScoreGauge from '../components/ScoreGauge';
import { CashFlowChart } from '../components/ProjectionChart';
import { getHealthScore, getCashFlowData } from '../api/client';
import { Link } from 'react-router-dom';
import { useProfile } from '../context/ProfileContext';
import ProfileModal from '../components/ProfileModal';

export default function Dashboard() {
  const { profile, setProfile } = useProfile();
  const [showProfileEdit, setShowProfileEdit] = useState(false);
  const [health, setHealth] = useState(null);
  const [cashflow, setCashflow] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getHealthScore().catch(() => null),
      getCashFlowData().catch(() => null),
    ]).then(([h, cf]) => {
      if (h?.data) setHealth(h.data);
      if (cf?.data) setCashflow(cf.data);
      setLoading(false);
    });
  }, []);

  const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

  return (
    <div className="layout-content" style={{ paddingTop: 'var(--stack-lg)' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
        {/* Header */}
        <div style={{ marginBottom: 'var(--stack-lg)' }}>
          <h1 className="text-headline-md" style={{ fontWeight: 700, marginBottom: 4 }}>Dashboard</h1>
          <p className="text-body-sm" style={{ color: 'var(--text-muted)' }}>Your financial health at a glance.</p>
        </div>

        {/* Profile Summary Bar */}
        {profile && (
          <div className="card" style={{
            display: 'flex', alignItems: 'center', gap: 20, marginBottom: 'var(--stack-lg)',
            padding: '14px 20px', background: 'rgba(139, 92, 246, 0.03)',
            border: '1px solid rgba(139, 92, 246, 0.12)',
          }}>
            <span className="material-symbols-outlined" style={{ color: 'var(--accent-violet)', fontSize: 20 }}>person</span>
            {[
              { label: 'Income', value: profile.income_monthly, icon: 'account_balance_wallet' },
              { label: 'Expenses', value: profile.monthly_expenses, icon: 'shopping_cart' },
              { label: 'Savings', value: profile.savings, icon: 'savings' },
            ].map((f) => (
              <div key={f.label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="text-label-caps" style={{ fontSize: 9, color: 'var(--text-muted)' }}>{f.label}</span>
                <span className="text-mono" style={{ fontWeight: 700, fontSize: 14 }}>₹{Number(f.value).toLocaleString('en-IN')}</span>
              </div>
            ))}
            <button
              className="btn btn-secondary"
              onClick={() => setShowProfileEdit(true)}
              style={{ marginLeft: 'auto', padding: '6px 12px', fontSize: 10 }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 14 }}>edit</span>
              Edit
            </button>
          </div>
        )}
        {showProfileEdit && (
          <ProfileModal onSave={(p) => { setProfile(p); setShowProfileEdit(false); }} />
        )}

        {/* Metrics row */}
        <div className="grid-4" style={{ marginBottom: 'var(--stack-lg)' }}>
          <MetricCard
            label="Current Balance"
            value={health ? fmt(health.balance) : '—'}
            icon="account_balance_wallet"
            color="var(--accent-blue)"
          />
          <MetricCard
            label="30-Day Inflow"
            value={health ? fmt(health.inflow_30d) : '—'}
            delta={health ? '+12%' : undefined}
            deltaType="positive"
            icon="trending_up"
            color="var(--accent-emerald)"
          />
          <MetricCard
            label="30-Day Outflow"
            value={health ? fmt(health.outflow_30d) : '—'}
            icon="trending_down"
            color="var(--accent-red)"
          />
          <MetricCard
            label="Predicted Balance"
            value={health ? fmt(health.predicted_balance) : '—'}
            icon="query_stats"
            color="var(--accent-violet)"
          />
        </div>

        {/* Chart + Gauge row */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--stack-md)', marginBottom: 'var(--stack-lg)' }}>
          {/* Chart */}
          <div className="card">
            <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>Cash Flow Trend</div>
            {loading ? (
              <div style={{ height: 360, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span className="text-body-sm" style={{ color: 'var(--text-muted)' }}>Loading chart data...</span>
              </div>
            ) : cashflow ? (
              <CashFlowChart historical={cashflow.historical} forecast={cashflow.forecast} />
            ) : (
              <div style={{ height: 360, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span className="text-body-sm" style={{ color: 'var(--text-muted)' }}>Start the API server to load data</span>
              </div>
            )}
          </div>

          {/* Health gauge */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 20 }}>Financial Health</div>
            <ScoreGauge score={health?.score || 0} />
            <p className="text-body-sm" style={{ color: 'var(--text-secondary)', marginTop: 16, textAlign: 'center' }}>
              {health?.score >= 70
                ? 'Your finances are in good shape. Keep it up!'
                : 'Consider reviewing your spending patterns.'}
            </p>
          </div>
        </div>

        {/* Quick actions */}
        <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 12 }}>Quick Actions</div>
        <div className="grid-4">
          {[
            { to: '/chat', icon: 'smart_toy', label: 'Ask FinPilot', color: 'var(--accent-violet)' },
            { to: '/boardroom', icon: 'groups', label: 'Run Boardroom', color: 'var(--accent-blue)' },
            { to: '/simulator', icon: 'calculate', label: 'Simulate Purchase', color: 'var(--accent-amber)' },
            { to: '/spending', icon: 'analytics', label: 'Spending Insights', color: 'var(--accent-emerald)' },
          ].map((a, i) => (
            <Link to={a.to} key={i} style={{ textDecoration: 'none' }}>
              <motion.div
                className="card"
                whileHover={{ scale: 1.02, borderColor: a.color }}
                style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }}
              >
                <span className="material-symbols-outlined" style={{ color: a.color }}>{a.icon}</span>
                <span className="text-body-sm" style={{ fontWeight: 500 }}>{a.label}</span>
                <span className="material-symbols-outlined" style={{ marginLeft: 'auto', fontSize: 16, color: 'var(--text-muted)' }}>arrow_forward</span>
              </motion.div>
            </Link>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
