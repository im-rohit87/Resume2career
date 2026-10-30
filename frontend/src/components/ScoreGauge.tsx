import React from 'react';

interface ScoreGaugeProps {
  score: number; // 0 to 100
  size?: number;
  strokeWidth?: number;
  label?: string;
  sublabel?: string;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  size = 140,
  strokeWidth = 10,
  label = 'Score',
  sublabel,
}) => {
  const safeScore = Math.max(0, Math.min(100, Math.round(score)));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (safeScore / 100) * circumference;

  let colorClass = 'text-emerald-500';
  let bgGlow = 'rgba(16, 185, 129, 0.15)';
  if (safeScore < 50) {
    colorClass = 'text-rose-500';
    bgGlow = 'rgba(244, 63, 94, 0.15)';
  } else if (safeScore < 75) {
    colorClass = 'text-amber-500';
    bgGlow = 'rgba(245, 158, 11, 0.15)';
  }

  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="rotate-[-90deg]">
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200"
          />
          {/* Filled Progress Arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${colorClass} transition-all duration-1000 ease-out`}
            style={{ filter: `drop-shadow(0 0 8px ${bgGlow})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold tracking-tight text-gray-900">{safeScore}</span>
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">/ 100</span>
        </div>
      </div>
      {label && <p className="mt-2 text-sm font-semibold text-gray-800">{label}</p>}
      {sublabel && <p className="text-xs text-gray-500 max-w-[160px]">{sublabel}</p>}
    </div>
  );
};
