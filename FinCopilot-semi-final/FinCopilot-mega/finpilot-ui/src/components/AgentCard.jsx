import { motion } from 'framer-motion';

export default function AgentCard({ agent, emoji, color, response, index = 0 }) {
  return (
    <motion.div
      className="agent-card"
      style={{ borderLeftColor: color }}
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: index * 0.15 }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        <span style={{ fontSize: 22 }}>{emoji}</span>
        <span style={{ fontWeight: 600, fontSize: 14, color: color }}>{agent}</span>
      </div>
      <div className="text-body-sm" style={{ color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
        {response}
      </div>
    </motion.div>
  );
}
