import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Area, AreaChart, Legend,
} from 'recharts';

const COLORS = {
  indigo:  '#818CF8',
  emerald: '#34D399',
  amber:   '#FBBF24',
  red:     '#F87171',
  violet:  '#8B5CF6',
};

function CustomTooltip({ active, payload, label, prefix = '₹' }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#1A1A1A', border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: 4, padding: '10px 14px', fontSize: 12,
    }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: 6 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontFamily: "'Geist', monospace" }}>
          {p.name}: {prefix}{Number(p.value).toLocaleString('en-IN')}
        </div>
      ))}
    </div>
  );
}

export function CashFlowChart({ historical = [], forecast = [] }) {
  const histData = historical.map(d => ({
    date: new Date(d.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    Historical: Math.round(d.balance),
  }));
  const forecastData = forecast.map(d => ({
    date: new Date(d.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    Predicted: Math.round(d.balance),
    Upper: Math.round(d.upper),
    Lower: Math.round(d.lower),
  }));

  const combined = [...histData, ...forecastData];

  return (
    <ResponsiveContainer width="100%" height={360}>
      <AreaChart data={combined} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
        <defs>
          <linearGradient id="confBand" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={COLORS.indigo} stopOpacity={0.12} />
            <stop offset="95%" stopColor={COLORS.indigo} stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
        <YAxis tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} tick={{ fontSize: 10 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Area type="monotone" dataKey="Upper" stroke="none" fill="url(#confBand)" name="Confidence" />
        <Line type="monotone" dataKey="Historical" stroke={COLORS.indigo} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="Predicted" stroke={COLORS.emerald} strokeWidth={2} strokeDasharray="6 4" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function ProjectionChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="month" tick={{ fontSize: 10 }} label={{ value: 'Month', position: 'insideBottom', offset: -4, fontSize: 11 }} />
        <YAxis tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} tick={{ fontSize: 10 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Line type="monotone" dataKey="control" name="No Purchase" stroke={COLORS.indigo} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="static" name="Static Model" stroke={COLORS.amber} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="ml_dynamic" name="ML Dynamic" stroke={COLORS.violet} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
