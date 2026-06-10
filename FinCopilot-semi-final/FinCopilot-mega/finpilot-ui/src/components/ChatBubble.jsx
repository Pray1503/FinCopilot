import { motion } from 'framer-motion';

export default function ChatBubble({ role, text, intent, children }) {
  const isUser = role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{ marginBottom: 12 }}
    >
      {!isUser && intent && (
        <div style={{ marginBottom: 4, marginLeft: 4 }}>
          <span className="intent-badge">{intent}</span>
        </div>
      )}
      <div className={isUser ? 'chat-user' : 'chat-ai'}>
        {text && <div style={{ whiteSpace: 'pre-wrap' }}>{text}</div>}
        {children}
      </div>
    </motion.div>
  );
}
