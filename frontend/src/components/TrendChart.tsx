import React from 'react';

interface TrendItem {
  session_number: number;
  title: string;
  date: string;
  score: number;
  readiness: number;
}

interface TrendChartProps {
  data: TrendItem[];
  height?: number;
}

export const TrendChart: React.FC<TrendChartProps> = ({ data, height = 220 }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-44 items-center justify-center rounded-xl border border-dashed border-gray-200 text-gray-400 text-sm">
        No completed interviews yet. Complete your first session to track trends!
      </div>
    );
  }

  const paddingLeft = 35;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 30;
  const width = 500; // viewBox width

  const plotWidth = width - paddingLeft - paddingRight;
  const plotHeight = height - paddingTop - paddingBottom;

  const maxScore = 100;
  const minScore = 0;

  // Calculate coordinates
  const points = data.map((d, i) => {
    const x = paddingLeft + (data.length === 1 ? plotWidth / 2 : (i / (data.length - 1)) * plotWidth);
    const yScore = paddingTop + plotHeight - (d.score / maxScore) * plotHeight;
    const yReadiness = paddingTop + plotHeight - (d.readiness / maxScore) * plotHeight;
    return { x, yScore, yReadiness, d };
  });

  const lineScorePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.yScore}`).join(' ');
  const areaScorePath = `${lineScorePath} L ${points[points.length - 1].x} ${paddingTop + plotHeight} L ${points[0].x} ${paddingTop + plotHeight} Z`;

  const lineReadinessPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.yReadiness}`).join(' ');

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3 text-xs font-medium text-gray-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-indigo-500"></span> Interview Score
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span> Readiness Index
          </span>
        </div>
        <span>Recent {data.length} Session(s)</span>
      </div>

      <div className="w-full overflow-hidden">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          <defs>
            <linearGradient id="scoreArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#6366f1" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map((val) => {
            const y = paddingTop + plotHeight - (val / 100) * plotHeight;
            return (
              <g key={val}>
                <line
                  x1={paddingLeft}
                  y1={y}
                  x2={width - paddingRight}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
                <text
                  x={paddingLeft - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="text-[9px] fill-gray-400 font-mono"
                >
                  {val}
                </text>
              </g>
            );
          })}

          {/* Score Area & Line */}
          <path d={areaScorePath} fill="url(#scoreArea)" />
          <path d={lineScorePath} fill="none" stroke="#6366f1" strokeWidth="2.5" strokeLinecap="round" />

          {/* Readiness Line */}
          <path d={lineReadinessPath} fill="none" stroke="#10b981" strokeWidth="2" strokeDasharray="4 3" strokeLinecap="round" />

          {/* Data Points */}
          {points.map((p, idx) => (
            <g key={idx}>
              <circle cx={p.x} cy={p.yScore} r={4} className="fill-indigo-500 stroke-white stroke-2" />
              <circle cx={p.x} cy={p.yReadiness} r={3} className="fill-emerald-400 stroke-white stroke-1" />
              <text
                x={p.x}
                y={paddingTop + plotHeight + 16}
                textAnchor="middle"
                className="text-[9px] fill-gray-500 font-medium"
              >
                #{p.d.session_number}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
};
