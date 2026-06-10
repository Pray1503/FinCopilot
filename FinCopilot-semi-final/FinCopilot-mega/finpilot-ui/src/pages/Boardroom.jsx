import { useState } from 'react';
import { motion } from 'framer-motion';
import AgentCard from '../components/AgentCard';
import { runBoardroom, runSmartBoardroom } from '../api/client';
import { useProfile } from '../context/ProfileContext';

const DEFAULT_SCENARIO = {
  income_monthly: 15000,
  monthly_expenses: 9000,
  savings: 20000,
  existing_debt_monthly_EMI: 0,
  requested_loan_amount: 50000,
  proposed_EMI: 2500,
  expected_skill_earning_uplift_pct: 20,
  emergency_fund_amount: 10000,
  course_length_months: 6,
};

const FIELDS = [
  { key: 'income_monthly', label: 'Monthly Income (₹)' },
  { key: 'monthly_expenses', label: 'Monthly Expenses (₹)' },
  { key: 'savings', label: 'Current Savings (₹)' },
  { key: 'proposed_EMI', label: 'Proposed EMI (₹)' },
  { key: 'requested_loan_amount', label: 'Loan Amount (₹)' },
  { key: 'emergency_fund_amount', label: 'Emergency Fund (₹)' },
];

export default function Boardroom() {
  const { profile } = useProfile();
  const [scenario, setScenario] = useState({
    ...DEFAULT_SCENARIO,
    ...(profile ? { income_monthly: profile.income_monthly, monthly_expenses: profile.monthly_expenses, savings: profile.savings, emergency_fund_amount: profile.savings } : {}),
  });
  const [question, setQuestion] = useState('Should I take this loan for a coding bootcamp?');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('smart'); // 'smart' (pure Python) or 'ai' (LLM)
  const [activeAgent, setActiveAgent] = useState(-1);

  const run = async () => {
    setLoading(true);
    setResult(null);
    setActiveAgent(0);
    try {
      const fn = mode === 'ai' ? runBoardroom : runSmartBoardroom;
      const { data } = await fn(scenario, question);
      setResult(data);
    } catch (err) {
      setResult({ error: err.message || 'Failed to run boardroom' });
    }
    setLoading(false);
  };

  const verdictClass = result?.verdict === 'Go_now' ? 'verdict-go'
    : result?.verdict === 'Delay_and_prepare' ? 'verdict-delay'
    : result?.verdict === 'Decline' ? 'verdict-decline' : '';

  const verdictEmoji = result?.verdict === 'Go_now' ? '✅'
    : result?.verdict === 'Delay_and_prepare' ? '⏸️' : '🛑';

  return (
    <div className="layout-content" style={{ paddingTop: 'var(--stack-lg)' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-blue)' }}>groups</span>
          <h1 className="text-headline-md" style={{ fontWeight: 700 }}>Financial Boardroom</h1>
        </div>
        <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginBottom: 'var(--stack-lg)' }}>
          Multi-agent AI panel analyzing your financial decisions.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 'var(--stack-lg)' }}>
          {/* Input Panel */}
          <div>
            <div className="card" style={{ marginBottom: 'var(--stack-md)' }}>
              <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 16 }}>Financial Profile</div>
              {FIELDS.map(f => (
                <div key={f.key} style={{ marginBottom: 12 }}>
                  <label className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4, display: 'block' }}>{f.label}</label>
                  <input
                    className="input"
                    type="number"
                    value={scenario[f.key]}
                    onChange={(e) => setScenario({ ...scenario, [f.key]: Number(e.target.value) })}
                  />
                </div>
              ))}
            </div>

            <div className="card" style={{ marginBottom: 'var(--stack-md)' }}>
              <label className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4, display: 'block' }}>Question</label>
              <textarea
                className="input"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={3}
                style={{ resize: 'vertical' }}
              />
            </div>

            {/* Mode toggle */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 'var(--stack-md)' }}>
              <button
                className={mode === 'smart' ? 'btn btn-primary' : 'btn btn-secondary'}
                onClick={() => setMode('smart')}
                style={{ flex: 1 }}
              >Smart (No LLM)</button>
              <button
                className={mode === 'ai' ? 'btn btn-ai' : 'btn btn-secondary'}
                onClick={() => setMode('ai')}
                style={{ flex: 1 }}
              >AI Debate</button>
            </div>

            <button
              className="btn btn-primary"
              onClick={run}
              disabled={loading}
              style={{ width: '100%', padding: '14px' }}
            >
              {loading ? 'Analyzing...' : 'Run Boardroom'}
              {!loading && <span className="material-symbols-outlined" style={{ fontSize: 16 }}>play_arrow</span>}
            </button>
          </div>

          {/* Results Panel */}
          <div>
            {!result && !loading && (
              <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
                <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--text-muted)', opacity: 0.3, marginBottom: 12, display: 'block' }}>groups</span>
                <p className="text-body-sm" style={{ color: 'var(--text-muted)' }}>
                  Configure your financial profile and click "Run Boardroom" to start the analysis.
                </p>
              </div>
            )}

            {loading && (
              <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
                <span className="material-symbols-outlined animate-pulse" style={{ fontSize: 36, color: 'var(--accent-violet)', marginBottom: 12, display: 'block' }}>psychology</span>
                <p className="text-body-sm" style={{ color: 'var(--text-muted)' }}>
                  {mode === 'ai' ? 'AI agents are debating...' : 'Running analysis...'}
                </p>
              </div>
            )}

            {result && !result.error && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                {/* Verdict */}
                <div className={`verdict-header ${verdictClass}`} style={{ marginBottom: 'var(--stack-md)' }}>
                  {verdictEmoji} {result.verdict?.replace(/_/g, ' ')}
                </div>

                {/* Agent timeline */}
                {result.turns && (
                  <div className="timeline" style={{ marginBottom: 'var(--stack-md)' }}>
                    {result.turns.map((t, i) => (
                      <span
                        key={i}
                        className={`timeline-node ${i === activeAgent ? 'active' : ''}`}
                        onClick={() => setActiveAgent(i)}
                        style={{ cursor: 'pointer' }}
                      >
                        {t.emoji} {t.agent}
                      </span>
                    ))}
                  </div>
                )}

                {/* Agent Cards — AI mode */}
                {result.turns && result.turns.map((t, i) => (
                  <AgentCard
                    key={i}
                    agent={t.agent}
                    emoji={t.emoji}
                    color={t.color}
                    response={t.response}
                    index={i}
                  />
                ))}

                {/* Smart mode results */}
                {result.coordinator && !result.turns && (
                  <>
                    <div className="card" style={{ marginBottom: 'var(--stack-md)' }}>
                      <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 12 }}>Coordinator Analysis</div>
                      <p className="text-body-sm" style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{result.coordinator.agrees}</p>
                      <div className="ai-reasoning" style={{ marginBottom: 12 }}>
                        <p className="text-mono" style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
                          {result.coordinator.coordinator_recommendation}
                        </p>
                      </div>
                      <p className="text-body-sm" style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>{result.coordinator.tradeoff}</p>
                    </div>

                    {/* Next Steps */}
                    {result.coordinator.next_steps && (
                      <div className="card">
                        <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 12 }}>Action Plan</div>
                        {result.coordinator.next_steps.map((step, i) => (
                          <div key={i} style={{
                            display: 'flex', gap: 12, alignItems: 'flex-start',
                            padding: '10px 14px', background: 'var(--bg-container)',
                            border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)',
                            marginBottom: 8,
                          }}>
                            <div style={{
                              width: 24, height: 24, borderRadius: '50%',
                              background: 'var(--accent-blue)', color: '#fff',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontSize: 12, fontWeight: 700, flexShrink: 0,
                            }}>{i + 1}</div>
                            <div>
                              <div className="text-body-sm" style={{ color: 'var(--text-secondary)' }}>{step.action}</div>
                              <div className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                                Within {step.timeframe_days} days
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </motion.div>
            )}

            {result?.error && (
              <div className="card" style={{ borderLeftColor: 'var(--accent-red)', borderLeftWidth: 3 }}>
                <p style={{ color: 'var(--accent-red)' }}>Error: {result.error}</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
