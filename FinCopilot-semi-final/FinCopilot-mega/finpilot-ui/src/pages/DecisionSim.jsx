import { useState } from 'react';
import { motion } from 'framer-motion';
import MetricCard from '../components/MetricCard';
import ScoreGauge from '../components/ScoreGauge';
import { ProjectionChart } from '../components/ProjectionChart';
import { runSimulator } from '../api/client';
import { useProfile } from '../context/ProfileContext';

const DEFAULT = {
  income: 15000,
  current_savings: 20000,
  base_expenses: 9000,
  item_name: 'Laptop',
  cost: 45000,
  goal_name: 'Savings Goal',
  goal_target: 100000,
  goal_current: 20000,
  goal_alloc: 3000,
};

const FIELDS = [
  { key: 'item_name', label: 'Item Name', type: 'text' },
  { key: 'cost', label: 'Item Cost (₹)', type: 'number' },
  { key: 'income', label: 'Monthly Income (₹)', type: 'number' },
  { key: 'base_expenses', label: 'Monthly Expenses (₹)', type: 'number' },
  { key: 'current_savings', label: 'Current Savings (₹)', type: 'number' },
  { key: 'goal_target', label: 'Goal Target (₹)', type: 'number' },
];

export default function DecisionSim() {
  const { profile } = useProfile();
  const [params, setParams] = useState({
    ...DEFAULT,
    ...(profile ? { income: profile.income_monthly, base_expenses: profile.monthly_expenses, current_savings: profile.savings, goal_current: profile.savings } : {}),
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const { data } = await runSimulator(params);
      setResult(data);
    } catch (err) {
      setResult({ error: err.message || 'Simulation failed' });
    }
    setLoading(false);
  };

  const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

  return (
    <div className="layout-content" style={{ paddingTop: 'var(--stack-lg)' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-amber)' }}>calculate</span>
          <h1 className="text-headline-md" style={{ fontWeight: 700 }}>Decision Simulator</h1>
        </div>
        <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginBottom: 'var(--stack-lg)' }}>
          Should you buy it? ML-powered 12-month projection with seasonal spending prediction.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 'var(--stack-lg)' }}>
          {/* Inputs */}
          <div>
            <div className="card">
              <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>Purchase Details</div>
              {FIELDS.map(f => (
                <div key={f.key} style={{ marginBottom: 12 }}>
                  <label className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4, display: 'block' }}>{f.label}</label>
                  <input
                    className="input"
                    type={f.type}
                    value={params[f.key]}
                    onChange={(e) => setParams({ ...params, [f.key]: f.type === 'number' ? Number(e.target.value) : e.target.value })}
                  />
                </div>
              ))}
              <button
                className="btn btn-primary"
                onClick={simulate}
                disabled={loading}
                style={{ width: '100%', marginTop: 8, padding: '14px' }}
              >
                {loading ? 'Simulating...' : 'Run Simulation'}
                {!loading && <span className="material-symbols-outlined" style={{ fontSize: 16 }}>play_arrow</span>}
              </button>
            </div>
          </div>

          {/* Results */}
          <div>
            {!result && !loading && (
              <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
                <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--text-muted)', opacity: 0.3, display: 'block', marginBottom: 12 }}>science</span>
                <p className="text-body-sm" style={{ color: 'var(--text-muted)' }}>
                  Enter your purchase details and click "Run Simulation" to see the impact.
                </p>
              </div>
            )}

            {loading && (
              <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
                <span className="material-symbols-outlined animate-pulse" style={{ fontSize: 36, color: 'var(--accent-amber)' }}>hourglass_empty</span>
                <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginTop: 12 }}>Running ML-powered simulation...</p>
              </div>
            )}

            {result && !result.error && (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
                {/* Verdict */}
                <div className={`verdict-header ${
                  result.affordability_score >= 70 ? 'verdict-go' :
                  result.affordability_score >= 45 ? 'verdict-delay' : 'verdict-decline'
                }`}>
                  {result.verdict}
                </div>

                {/* Metrics */}
                <div className="grid-4" style={{ marginBottom: 'var(--stack-md)' }}>
                  <div style={{ display: 'flex', justifyContent: 'center' }}>
                    <ScoreGauge score={result.affordability_score} size={140} label="Affordability" />
                  </div>
                  <MetricCard label="Monthly Surplus" value={fmt(result.surplus)} color="var(--accent-emerald)" />
                  <MetricCard label="Time to Absorb" value={`${result.months_to_absorb} months`} color="var(--accent-amber)" />
                  <MetricCard label="Goal Delay" value={`+${result.freeze_months} months`} color="var(--accent-red)" />
                </div>

                {/* Projection Chart */}
                <div className="card" style={{ marginBottom: 'var(--stack-md)' }}>
                  <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>12-Month Savings Projection</div>
                  <ProjectionChart data={result.projections} />
                </div>

                {/* Goal Impact */}
                <div className="card">
                  <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 12 }}>Goal Impact — {result.goal_name}</div>
                  <div className="grid-3">
                    <MetricCard label="Original Timeline" value={`${result.original_timeline} months`} />
                    <MetricCard label="Delayed Timeline" value={`${result.delayed_timeline} months`} color="var(--accent-amber)" />
                    <MetricCard label="Item Cost" value={fmt(result.cost)} />
                  </div>
                </div>
              </motion.div>
            )}

            {result?.error && (
              <div className="card" style={{ borderLeftColor: 'var(--accent-red)', borderLeftWidth: 3 }}>
                <p style={{ color: 'var(--accent-red)' }}>{result.error || result.message}</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
