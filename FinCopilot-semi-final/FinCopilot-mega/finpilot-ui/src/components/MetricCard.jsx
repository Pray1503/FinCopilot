import { motion } from 'framer-motion';

export default function MetricCard({ label, value, delta, deltaType = 'positive', icon, color }) {
  return (
    <motion.div
      className="metric-card"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ borderColor: color || 'rgba(139,92,246,0.2)', boxShadow: '0 0 30px rgba(139,92,246,0.06)' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div className="label">{label}</div>
        {icon && (
          <span className="material-symbols-outlined" style={{ fontSize: 18, color: color || 'var(--text-muted)' }}>
            {icon}
          </span>
        )}
      </div>
      <div className="value" style={color ? { color } : {}}>{value}</div>
      {delta && (
        <div className={`delta ${deltaType === 'positive' ? 'delta-positive' : 'delta-negative'}`}>
          {deltaType === 'positive' ? '↑' : '↓'} {delta}
        </div>
      )}
    </motion.div>
  );
}
