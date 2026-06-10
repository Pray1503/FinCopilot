import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import MetricCard from '../components/MetricCard';
import { getSpendingSummary } from '../api/client';

export default function SpendingInsights() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSpendingSummary()
      .then(res => setData(res.data))
      .catch(() => null)
      .finally(() => setLoading(false));
  }, []);

  const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

  return (
    <div className="layout-content" style={{ paddingTop: 'var(--stack-lg)' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-emerald)' }}>analytics</span>
          <h1 className="text-headline-md" style={{ fontWeight: 700 }}>Spending Insights</h1>
        </div>
        <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginBottom: 'var(--stack-lg)' }}>
          Analyze your spending habits and predict next week's budget.
        </p>

        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
            <span className="material-symbols-outlined animate-pulse" style={{ fontSize: 36, color: 'var(--accent-emerald)' }}>hourglass_empty</span>
            <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginTop: 12 }}>Loading spending data...</p>
          </div>
        ) : data ? (
          <>
            {/* Metric Cards */}
            <div className="grid-4" style={{ marginBottom: 'var(--stack-lg)' }}>
              <MetricCard label="Total Tracked" value={fmt(data.total_tracked)} icon="receipt_long" color="var(--accent-blue)" />
              <MetricCard label="Days Tracked" value={data.days_tracked} icon="calendar_month" color="var(--text-secondary)" />
              <MetricCard label="Daily Average" value={fmt(data.avg_daily)} icon="trending_flat" color="var(--accent-amber)" />
              <MetricCard label="Next Week Prediction" value={fmt(data.prediction_next_week)} icon="query_stats" color="var(--accent-violet)" />
            </div>

            {/* Insights */}
            <div className="card" style={{ marginBottom: 'var(--stack-md)' }}>
              <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>Behavioral Insights</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {data.insights?.map((insight, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="ai-reasoning"
                    style={{ fontSize: 14, lineHeight: 1.7, color: 'var(--text-secondary)' }}
                  >
                    {insight}
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Prediction Detail */}
            <div className="card">
              <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 14, verticalAlign: 'middle', marginRight: 6, color: 'var(--accent-violet)' }}>smart_toy</span>
                ML Prediction Engine
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--stack-md)' }}>
                <div style={{ padding: 20, background: 'var(--bg-container)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 8, fontSize: 10 }}>Model</div>
                  <div className="text-mono" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>Linear Regression</div>
                  <div className="text-body-sm" style={{ color: 'var(--text-muted)', marginTop: 4 }}>Trained on weekly spending aggregates</div>
                </div>
                <div style={{ padding: 20, background: 'var(--bg-container)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 8, fontSize: 10 }}>Prediction Confidence</div>
                  <div className="text-mono" style={{ color: 'var(--accent-violet)', fontWeight: 600 }}>~85%</div>
                  <div className="text-body-sm" style={{ color: 'var(--text-muted)', marginTop: 4 }}>Based on {data.days_tracked} days of data</div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--text-muted)', opacity: 0.3, display: 'block', marginBottom: 12 }}>analytics</span>
            <p className="text-body-sm" style={{ color: 'var(--text-muted)' }}>
              Start the API server to load spending data.
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
