import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const FEATURES = [
  { icon: 'smart_toy', title: 'Copilot Chat', desc: 'Ask any financial question. AI detects intent and routes to the right expert.', badge: 'AI', to: '/chat' },
  { icon: 'groups', title: 'Financial Boardroom', desc: '5-agent LLM debate: Budget-Bot, Risk-Radar, Planner, Chairman, and Devil\'s Advocate.', badge: 'AI', to: '/boardroom' },
  { icon: 'monitoring', title: 'Cash Flow Forecast', desc: 'Interactive dashboard with forecasting, budgets, scenario analysis, and health score.', badge: 'LIVE', to: '/cashflow' },
  { icon: 'calculate', title: 'Decision Simulator', desc: 'Should you buy it? ML-powered 12-month projection with seasonal spending prediction.', badge: 'ML', to: '/simulator' },
  { icon: 'analytics', title: 'Spending Insights', desc: 'Analyse spending habits, identify weekend burn, and predict next week\'s budget.', badge: 'ML', to: '/spending' },
  { icon: 'receipt_long', title: 'Bill Scanner', desc: 'Upload receipts and bills. OCR extracts vendor, amount, date, and category.', badge: 'AI', to: '/bills' },
];

const AGENTS = [
  { icon: 'account_balance', name: 'The Strategist', score: 85, quote: '"ROI is optimized."' },
  { icon: 'monitoring', name: 'Risk Manager', score: 92, quote: '"Low volatility path."' },
  { icon: 'payments', name: 'Tax Auditor', score: 45, quote: '"Credits available."' },
];

export default function Landing() {
  return (
    <div style={{ background: 'var(--bg-void)' }}>
      {/* Navbar */}
      <header className="navbar" style={{ justifyContent: 'space-between', maxWidth: 'var(--container-max)', margin: '0 auto', background: 'transparent' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--stack-sm)' }}>
          <div style={{
            width: 32, height: 32, borderRadius: 'var(--radius-sm)',
            background: 'var(--accent-violet)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
          }}>
            <span className="material-symbols-outlined" style={{ fontSize: 18, color: '#fff' }}>rocket_launch</span>
          </div>
          <span className="text-headline-sm" style={{ fontWeight: 600 }}>FinPilot</span>
        </div>
        <nav style={{ display: 'flex', alignItems: 'center', gap: 'var(--stack-lg)' }}>
          <Link to="/simulator" className="text-label-caps" style={{ color: 'var(--text-secondary)' }}>Simulator</Link>
          <Link to="/boardroom" className="text-label-caps" style={{ color: 'var(--text-secondary)' }}>Boardroom</Link>
          <Link to="/cashflow" className="text-label-caps" style={{ color: 'var(--text-secondary)' }}>Cash Flow</Link>
          <span style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 12px', background: 'var(--bg-high)', borderRadius: 'var(--radius-pill)',
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--secondary)' }} className="animate-pulse" />
            <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--secondary)' }}>AI Active</span>
          </span>
          <Link to="/dashboard" className="btn btn-primary" style={{ padding: '8px 16px' }}>Dashboard</Link>
        </nav>
      </header>

      {/* Hero */}
      <section style={{
        minHeight: '90vh', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', textAlign: 'center',
        padding: '64px var(--gutter) 0',
      }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          style={{ maxWidth: '800px' }}
        >
          <div className="animate-float" style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '8px 16px', background: 'var(--bg-container)',
            border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-pill)',
            marginBottom: 'var(--stack-lg)',
          }}>
            <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>auto_awesome</span>
            <span className="text-label-caps" style={{ color: 'var(--text-secondary)', fontSize: 11 }}>The Future of Student Finance</span>
          </div>

          <h1 className="text-display-lg" style={{ fontSize: 'clamp(40px, 6vw, 80px)', marginBottom: 'var(--stack-md)', letterSpacing: '-0.03em' }}>
            See The Future <br />
            <span style={{ color: 'var(--text-secondary)' }}>Before You Spend.</span>
          </h1>

          <p className="text-body-lg" style={{ color: 'var(--text-secondary)', maxWidth: 640, margin: '0 auto var(--stack-lg)' }}>
            FinPilot combines simulations, forecasting, OCR intelligence, spending analytics, and AI reasoning to help scholars make smarter financial decisions.
          </p>

          <div style={{ display: 'flex', gap: 'var(--stack-md)', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/dashboard" className="btn btn-primary" style={{ padding: '14px 32px' }}>
              Try FinPilot <span className="material-symbols-outlined" style={{ fontSize: 18 }}>arrow_forward</span>
            </Link>
            <Link to="/boardroom" className="btn btn-secondary" style={{ padding: '14px 32px' }}>
              View Financial Boardroom
            </Link>
          </div>
        </motion.div>

        {/* OS Interface Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="glass-panel"
          style={{
            marginTop: 60, width: '100%', maxWidth: 1000,
            borderRadius: '12px 12px 0 0', overflow: 'hidden',
            boxShadow: '0 -20px 60px rgba(139,92,246,0.06)',
          }}
        >
          {/* Title bar */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '0 16px', height: 40, borderBottom: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'rgba(248,113,113,0.3)' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'rgba(251,191,36,0.3)' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'rgba(52,211,153,0.3)' }} />
            </div>
            <div style={{ flex: 1, textAlign: 'center', fontSize: 10, color: 'var(--text-faint)', fontFamily: "'Geist', monospace" }}>
              FINPILOT_OS_V2.04
            </div>
          </div>
          {/* Dashboard mockup */}
          <div style={{ padding: 'var(--gutter)', display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--stack-md)' }}>
            <div>
              <div style={{ background: 'var(--bg-container)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: 16, marginBottom: 'var(--stack-md)' }}>
                <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 12, fontSize: 10 }}>Cash Flow Forecast</div>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 64 }}>
                  {[40, 60, 85, 70, 50, 45].map((h, i) => (
                    <div key={i} style={{
                      flex: 1, height: `${h}%`, borderRadius: 2,
                      background: i < 4 ? `rgba(192,193,255,${0.2 + i * 0.2})` : 'none',
                      borderTop: i >= 4 ? '1px dashed var(--secondary)' : 'none',
                    }} />
                  ))}
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--stack-md)' }}>
                <div style={{ background: 'var(--bg-container)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: 16 }}>
                  <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 12, fontSize: 10 }}>Budgets</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {[100, 80, 65].map((w, i) => (
                      <div key={i} style={{ height: 6, background: 'var(--bg-high)', borderRadius: 'var(--radius-pill)', width: `${w}%` }} />
                    ))}
                  </div>
                </div>
                <div style={{ background: 'var(--bg-container)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: 16 }}>
                  <div className="text-label-caps" style={{ color: 'var(--text-muted)', marginBottom: 12, fontSize: 10 }}>Simulation Runner</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ height: 24, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }} />
                    <div style={{ height: 24, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }} />
                  </div>
                </div>
              </div>
            </div>
            {/* AI Sidebar */}
            <div style={{ background: 'var(--bg-container)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>smart_toy</span>
                <span className="text-label-caps" style={{ fontSize: 10 }}>FinPilot Reasoning</span>
              </div>
              <div className="ai-reasoning" style={{ marginBottom: 12, fontSize: 11, fontFamily: "'Geist', monospace", color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                &gt; Analyzing loan restructuring...<br />
                &gt; Potential savings identified: ₹14k/yr.<br />
                &gt; Confidence score: 94%.
              </div>
              <div style={{ background: 'var(--bg-high)', borderRadius: 'var(--radius-sm)', padding: 12, fontSize: 11, color: 'var(--text-secondary)' }}>
                "If you proceed with the boardroom decision, your runway increases by 4 months."
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Boardroom Feature */}
      <section style={{ padding: '80px var(--gutter)', maxWidth: 'var(--container-max)', margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--stack-lg)', alignItems: 'center' }}>
          <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <span className="text-label-caps" style={{ color: 'var(--secondary)', marginBottom: 8, display: 'block' }}>Featured Tool</span>
            <h2 style={{ fontSize: 36, fontWeight: 700, marginBottom: 16 }}>The Financial Boardroom</h2>
            <p className="text-body-lg" style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
              Don't make big financial moves alone. Present your decision to a panel of AI financial specialists.
              Each expert analyzes your data through a unique lens before delivering a final verdict.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                { icon: 'groups', title: 'Multi-Agent Analysis', desc: 'Simultaneous review by five distinct AI personas.' },
                { icon: 'rule', title: 'Consensus Verdict', desc: 'Receive a final Go/No-Go score based on long-term health.' },
              ].map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 'var(--radius-sm)',
                    background: 'var(--bg-high)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    border: '1px solid var(--border-subtle)', flexShrink: 0,
                  }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 20 }}>{f.icon}</span>
                  </div>
                  <div>
                    <div className="text-label-caps" style={{ marginBottom: 4 }}>{f.title}</div>
                    <div className="text-body-sm" style={{ color: 'var(--text-secondary)' }}>{f.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Agent grid */}
          <motion.div
            initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}
            style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--stack-md)' }}
          >
            {AGENTS.map((a, i) => (
              <div key={i} style={{
                padding: 24, background: 'var(--bg-container)',
                border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)',
                textAlign: 'center', transition: 'border-color 0.3s',
              }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(192,193,255,0.3)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
              >
                <div style={{
                  width: 48, height: 48, borderRadius: '50%',
                  background: 'rgba(192,193,255,0.08)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center', margin: '0 auto 8px',
                }}>
                  <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>{a.icon}</span>
                </div>
                <div className="text-label-caps" style={{ marginBottom: 8 }}>{a.name}</div>
                <div style={{
                  height: 4, background: 'var(--bg-high)', borderRadius: 'var(--radius-pill)',
                  overflow: 'hidden', margin: '8px 0',
                }}>
                  <div style={{ width: `${a.score}%`, height: '100%', background: 'var(--secondary)', transition: 'width 1s ease' }} />
                </div>
                <div className="text-mono" style={{ fontSize: 10, color: 'var(--text-secondary)', fontStyle: 'italic' }}>{a.quote}</div>
              </div>
            ))}
            <div style={{
              padding: 24, background: 'var(--secondary)', borderRadius: 'var(--radius-sm)',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            }}>
              <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--bg-void)', opacity: 0.7 }}>Boardroom Verdict</span>
              <span style={{ fontSize: 40, fontWeight: 700, color: 'var(--bg-void)' }}>9.2</span>
              <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--bg-void)' }}>Strongly Approve</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Bento Feature Grid */}
      <section style={{ background: 'rgba(28,27,27,0.4)', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)', padding: '80px 0' }}>
        <div style={{ maxWidth: 'var(--container-max)', margin: '0 auto', padding: '0 var(--gutter)' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h3 className="text-headline-md" style={{ fontWeight: 700, marginBottom: 8 }}>High Performance Financial Intelligence</h3>
            <p className="text-body-sm" style={{ color: 'var(--text-secondary)' }}>Precision tools designed for the modern scholar's economy.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--stack-md)' }}>
            {FEATURES.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                <Link to={f.to} style={{ textDecoration: 'none' }}>
                  <div className="glass-panel" style={{
                    padding: 28, borderRadius: 'var(--radius-sm)',
                    cursor: 'pointer', transition: 'all 0.3s ease', height: '100%',
                  }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(139,92,246,0.3)'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; e.currentTarget.style.transform = 'translateY(0)'; }}
                  >
                    <span className="material-symbols-outlined" style={{ color: 'var(--secondary)', marginBottom: 12, display: 'block' }}>{f.icon}</span>
                    <h4 className="text-headline-sm" style={{ fontWeight: 700, marginBottom: 8 }}>{f.title}</h4>
                    <p className="text-body-sm" style={{ color: 'var(--text-secondary)' }}>{f.desc}</p>
                    <span className="text-label-caps" style={{
                      display: 'inline-block', marginTop: 16, padding: '4px 10px',
                      borderRadius: 'var(--radius-pill)', fontSize: 10,
                      background: f.badge === 'AI' ? 'rgba(99,102,241,0.1)' : f.badge === 'ML' ? 'rgba(139,92,246,0.1)' : 'rgba(52,211,153,0.1)',
                      color: f.badge === 'AI' ? 'var(--accent-blue)' : f.badge === 'ML' ? 'var(--accent-violet)' : 'var(--accent-emerald)',
                    }}>{f.badge}</span>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '120px var(--gutter)', textAlign: 'center' }}>
        <div style={{ maxWidth: 700, margin: '0 auto' }}>
          <h2 className="text-display-lg" style={{ fontWeight: 700, marginBottom: 16 }}>Start Your Financial OS.</h2>
          <p className="text-body-lg" style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>
            Join thousands of students building their future with AI-guided precision.
          </p>
          <div style={{ display: 'flex', gap: 'var(--stack-md)', justifyContent: 'center' }}>
            <Link to="/dashboard" className="btn btn-primary" style={{ padding: '14px 40px' }}>Initialize FinPilot</Link>
            <Link to="/chat" className="btn btn-secondary" style={{ padding: '14px 40px' }}>Talk to FinPilot</Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '48px var(--gutter)' }}>
        <div style={{ maxWidth: 'var(--container-max)', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)' }}>© 2025 FinPilot AI OS. All Rights Reserved.</span>
          <div style={{ display: 'flex', gap: 'var(--stack-lg)' }}>
            <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)', cursor: 'pointer' }}>Twitter</span>
            <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)', cursor: 'pointer' }}>GitHub</span>
            <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)', cursor: 'pointer' }}>Discord</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
