import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import ChatBubble from '../components/ChatBubble';
import { copilotChat } from '../api/client';
import { useProfile } from '../context/ProfileContext';

const SUGGESTIONS = [
  'Can I afford a ₹45,000 laptop?',
  'Analyze my budget using 50/30/20',
  'What\'s my cash flow forecast?',
  'Should I take a student loan?',
  'How are my spending habits?',
];

export default function CopilotChat() {
  const { profile } = useProfile();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    const query = text || input.trim();
    if (!query || loading) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setLoading(true);

    try {
      const { data } = await copilotChat(query, profile);
      setMessages(prev => [...prev, {
        role: 'ai',
        text: data.response,
        intent: data.intent,
        featureHtml: data.feature_html,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'ai',
        text: 'Sorry, I couldn\'t connect to the backend. Make sure the API server is running on port 8000.',
        intent: 'error',
      }]);
    }
    setLoading(false);
  };

  return (
    <div className="layout-content" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 0px)', paddingBottom: 0 }}>
      {/* Header */}
      <div style={{ marginBottom: 'var(--stack-md)', paddingTop: 'var(--stack-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--accent-violet)' }}>smart_toy</span>
          <h1 className="text-headline-md" style={{ fontWeight: 700 }}>FinPilot Copilot</h1>
        </div>
        <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginTop: 4 }}>
          Ask any financial question — AI detects intent and routes to the right expert.
        </p>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: 'var(--stack-md)' }}>
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ textAlign: 'center', padding: '60px 0' }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--accent-violet)', marginBottom: 16, display: 'block', opacity: 0.4 }}>psychology</span>
            <h3 className="text-headline-sm" style={{ marginBottom: 8, color: 'var(--text-secondary)' }}>What can I help you with?</h3>
            <p className="text-body-sm" style={{ color: 'var(--text-muted)', marginBottom: 24 }}>Try one of these suggestions:</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="btn btn-secondary"
                  onClick={() => sendMessage(s)}
                  style={{ fontSize: 12, padding: '8px 14px', textTransform: 'none', letterSpacing: 0 }}
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {messages.map((msg, i) => (
          <ChatBubble key={i} role={msg.role} text={msg.text} intent={msg.intent}>
            {msg.featureHtml && (
              <div
                style={{ marginTop: 12 }}
                dangerouslySetInnerHTML={{ __html: msg.featureHtml }}
              />
            )}
          </ChatBubble>
        ))}

        {loading && (
          <div style={{ padding: '8px 0' }}>
            <div className="chat-ai" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="animate-pulse" style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                FinPilot is thinking...
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '16px 0', borderTop: '1px solid var(--border-subtle)',
        background: 'var(--bg-void)',
      }}>
        <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} style={{ display: 'flex', gap: 8 }}>
          <input
            className="input input-pill"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask FinPilot anything..."
            disabled={loading}
            style={{ flex: 1 }}
          />
          <button
            type="submit"
            className="btn btn-ai"
            disabled={loading || !input.trim()}
            style={{ borderRadius: 'var(--radius-pill)', padding: '12px 20px' }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>send</span>
          </button>
        </form>
      </div>
    </div>
  );
}
