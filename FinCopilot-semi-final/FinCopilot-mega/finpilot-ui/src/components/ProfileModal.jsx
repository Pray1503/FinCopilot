import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const FIELDS = [
  { key: 'income_monthly', label: 'Monthly Income', icon: 'account_balance_wallet', placeholder: '15000', hint: 'Salary, stipend, pocket money...' },
  { key: 'monthly_expenses', label: 'Monthly Expenses', icon: 'shopping_cart', placeholder: '9000', hint: 'Rent, food, subscriptions...' },
  { key: 'savings', label: 'Liquid Savings', icon: 'savings', placeholder: '20000', hint: 'Bank balance, FD, easily accessible...' },
];

export default function ProfileModal({ onSave }) {
  const [values, setValues] = useState({ income_monthly: '', monthly_expenses: '', savings: '' });
  const [step, setStep] = useState(0); // 0 = intro, 1 = form

  const handleChange = (key, val) => {
    // Allow only digits
    setValues((prev) => ({ ...prev, [key]: val.replace(/[^\d]/g, '') }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      income_monthly: Number(values.income_monthly) || 15000,
      monthly_expenses: Number(values.monthly_expenses) || 9000,
      savings: Number(values.savings) || 20000,
    });
  };

  const allFilled = FIELDS.every((f) => values[f.key] && Number(values[f.key]) > 0);

  return (
    <AnimatePresence>
      <motion.div
        className="profile-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <motion.div
          className="profile-modal"
          initial={{ opacity: 0, scale: 0.92, y: 24 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.92, y: 24 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
        >
          {step === 0 ? (
            /* ── Intro ─────────────────────────────────────── */
            <motion.div key="intro" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="profile-intro">
              <div className="profile-logo">
                <span className="material-symbols-outlined" style={{ fontSize: 32, color: 'var(--accent-violet)' }}>rocket_launch</span>
              </div>
              <h2 className="text-headline-md" style={{ fontWeight: 700, marginBottom: 8 }}>Welcome to FinPilot</h2>
              <p className="text-body-sm" style={{ color: 'var(--text-muted)', lineHeight: 1.7, maxWidth: 340, margin: '0 auto 28px' }}>
                We need <strong style={{ color: 'var(--text-secondary)' }}>3 quick numbers</strong> to personalize your AI financial copilot.
                <br />Takes ~10 seconds.
              </p>
              <button className="btn btn-ai profile-cta" onClick={() => setStep(1)}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_forward</span>
                Let's Go
              </button>
            </motion.div>
          ) : (
            /* ── Form ──────────────────────────────────────── */
            <motion.form
              key="form"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25 }}
              onSubmit={handleSubmit}
              className="profile-form"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--accent-cyan)' }}>tune</span>
                <span className="text-label-caps" style={{ fontSize: 10, color: 'var(--text-muted)' }}>Financial Profile</span>
              </div>
              <h3 className="text-headline-sm" style={{ fontWeight: 700, marginBottom: 20 }}>Your Numbers</h3>

              <div className="profile-fields">
                {FIELDS.map((field, i) => (
                  <motion.div
                    key={field.key}
                    className="profile-field"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.08 }}
                  >
                    <div className="profile-field-header">
                      <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--accent-cyan)' }}>{field.icon}</span>
                      <label className="text-label-caps" style={{ fontSize: 10 }}>{field.label}</label>
                    </div>
                    <div className="profile-input-wrap">
                      <span className="profile-currency">₹</span>
                      <input
                        type="text"
                        inputMode="numeric"
                        className="profile-input"
                        placeholder={field.placeholder}
                        value={values[field.key]}
                        onChange={(e) => handleChange(field.key, e.target.value)}
                        autoFocus={i === 0}
                      />
                    </div>
                    <span className="profile-hint">{field.hint}</span>
                  </motion.div>
                ))}
              </div>

              <button
                type="submit"
                className={`btn profile-submit ${allFilled ? 'btn-ai' : ''}`}
                disabled={!allFilled}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>check</span>
                Start FinPilot
              </button>
            </motion.form>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
