import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import MetricCard from '../components/MetricCard';
import ScoreGauge from '../components/ScoreGauge';
import { CashFlowChart } from '../components/ProjectionChart';
import { getCashFlowData, getTransactions, getHealthScore } from '../api/client';

export default function CashFlow() {
  const [cashflow, setCashflow] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getCashFlowData().catch(() => null),
      getTransactions().catch(() => null),
      getHealthScore().catch(() => null),
    ]).then(([cf, tx, h]) => {
      if (cf?.data) setCashflow(cf.data);
      if (tx?.data) setTransactions(tx.data.transactions?.slice(0, 20) || []);
      if (h?.data) setHealth(h.data);
      setLoading(false);
    });
  }, []);

  const fmt = (v) => `₹${Number(v).toLocaleString('en-IN')}`;

  return (
    <div className="layout-content" style={{ paddingTop: 'var(--stack-lg)' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-blue)' }}>monitoring</span>
          <h1 className="text-headline-md" style={{ fontWeight: 700 }}>Cash Flow</h1>
        </div>
        <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginBottom: 'var(--stack-lg)' }}>
          Monitor your inflows, outflows, and forecast your financial runway.
        </p>

        {/* Metrics */}
        <div className="grid-4" style={{ marginBottom: 'var(--stack-lg)' }}>
          <MetricCard label="Balance" value={health ? fmt(health.balance) : '—'} icon="account_balance_wallet" color="var(--accent-blue)" />
          <MetricCard label="30d Inflow" value={health ? fmt(health.inflow_30d) : '—'} icon="trending_up" color="var(--accent-emerald)" />
          <MetricCard label="30d Outflow" value={health ? fmt(health.outflow_30d) : '—'} icon="trending_down" color="var(--accent-red)" />
          <MetricCard label="Net 30d" value={health ? fmt(health.net_30d) : '—'} icon="balance" color={health?.net_30d >= 0 ? 'var(--accent-emerald)' : 'var(--accent-red)'} />
        </div>

        {/* Chart + Gauge */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--stack-md)', marginBottom: 'var(--stack-lg)' }}>
          <div className="card">
            <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>Cash Flow Trend + Forecast</div>
            {cashflow ? (
              <CashFlowChart historical={cashflow.historical} forecast={cashflow.forecast} />
            ) : (
              <div style={{ height: 360, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span className="text-body-sm" style={{ color: 'var(--text-muted)' }}>{loading ? 'Loading...' : 'Start API server for data'}</span>
              </div>
            )}
          </div>
          <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 20 }}>Financial Health</div>
            <ScoreGauge score={health?.score || 0} />
          </div>
        </div>

        {/* Transactions */}
        <div className="card">
          <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>Recent Transactions</div>
          {transactions.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    {['Date', 'Category', 'Description', 'Type', 'Amount', 'Balance'].map(h => (
                      <th key={h} className="text-label-caps" style={{
                        textAlign: 'left', padding: '8px 12px', fontSize: 10,
                        color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)',
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td className="text-mono" style={{ padding: '8px 12px', fontSize: 12 }}>{tx.Date}</td>
                      <td style={{ padding: '8px 12px', fontSize: 12 }}>{tx.Category}</td>
                      <td className="text-body-sm" style={{ padding: '8px 12px', color: 'var(--text-secondary)' }}>{tx.Description}</td>
                      <td style={{ padding: '8px 12px' }}>
                        <span style={{
                          fontSize: 10, fontWeight: 600, padding: '2px 8px',
                          borderRadius: 'var(--radius-pill)',
                          background: tx.Type === 'Income' ? 'rgba(52,211,153,0.1)' : 'rgba(248,113,113,0.1)',
                          color: tx.Type === 'Income' ? 'var(--accent-emerald)' : 'var(--accent-red)',
                        }}>{tx.Type}</span>
                      </td>
                      <td className="text-mono" style={{
                        padding: '8px 12px', fontSize: 13, fontWeight: 600,
                        color: tx.Amount >= 0 ? 'var(--accent-emerald)' : 'var(--accent-red)',
                      }}>
                        {tx.Amount >= 0 ? '+' : ''}{fmt(tx.Amount)}
                      </td>
                      <td className="text-mono" style={{ padding: '8px 12px', fontSize: 12, color: 'var(--text-secondary)' }}>{fmt(tx.Balance)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-body-sm" style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 24 }}>
              {loading ? 'Loading transactions...' : 'No transactions available.'}
            </p>
          )}
        </div>
      </motion.div>
    </div>
  );
}
