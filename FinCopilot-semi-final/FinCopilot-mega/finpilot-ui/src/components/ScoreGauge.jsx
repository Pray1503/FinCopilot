import { useEffect, useState } from 'react';

export default function ScoreGauge({ score = 0, size = 180, label = '' }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  let color, statusLabel;
  if (score >= 85)      { color = 'var(--accent-emerald)'; statusLabel = 'Excellent'; }
  else if (score >= 70) { color = 'var(--accent-blue)';    statusLabel = 'Good'; }
  else if (score >= 50) { color = 'var(--accent-amber)';   statusLabel = 'Average'; }
  else                  { color = 'var(--accent-red)';     statusLabel = 'Risky'; }

  return (
    <div className="gauge-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle className="gauge-bg" cx={size/2} cy={size/2} r={radius} />
        <circle
          className="gauge-fill"
          cx={size/2} cy={size/2} r={radius}
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="gauge-value">
        <div className="number" style={{ color }}>{score}</div>
        <div className="label">{label || statusLabel}</div>
      </div>
    </div>
  );
}
