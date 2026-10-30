import React from 'react';

interface RadarChartProps {
  data: {
    relevance: number;
    technical: number;
    completeness: number;
    clarity: number;
    reasoning: number;
  };
  size?: number;
}

export const RadarChart: React.FC<RadarChartProps> = ({ data, size = 320 }) => {
  const center = size / 2;
  const radius = (size / 2) - 45;

  const axes = [
    { key: 'relevance', label: 'Relevance', value: data.relevance },
    { key: 'technical', label: 'Technical Depth', value: data.technical },
    { key: 'completeness', label: 'Completeness', value: data.completeness },
    { key: 'clarity', label: 'Clarity & Style', value: data.clarity },
    { key: 'reasoning', label: 'Reasoning', value: data.reasoning },
  ];

  const totalAxes = axes.length;
  const angleStep = (Math.PI * 2) / totalAxes;

  // Generate concentric level polygon points (20, 40, 60, 80, 100%)
  const levels = [0.2, 0.4, 0.6, 0.8, 1.0];
  const levelPolygons = levels.map((lvl) => {
    return axes
      .map((_, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const x = center + radius * lvl * Math.cos(angle);
        const y = center + radius * lvl * Math.sin(angle);
        return `${x},${y}`;
      })
      .join(' ');
  });

  // Calculate candidate points
  const candidatePoints = axes
    .map((axis, i) => {
      const normalized = Math.max(0, Math.min(100, axis.value)) / 100;
      const angle = i * angleStep - Math.PI / 2;
      const x = center + radius * normalized * Math.cos(angle);
      const y = center + radius * normalized * Math.sin(angle);
      return { x, y, val: Math.round(axis.value) };
    });

  const polygonString = candidatePoints.map((p) => `${p.x},${p.y}`).join(' ');

  return (
    <div className="flex flex-col items-center justify-center p-2">
      <svg width={size} height={size} className="overflow-visible">
        <defs>
          <radialGradient id="radarFill" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#818cf8" stopOpacity="0.15" />
          </radialGradient>
        </defs>

        {/* Concentric Grid Polygons */}
        {levelPolygons.map((pts, idx) => (
          <polygon
            key={idx}
            points={pts}
            fill="transparent"
            stroke="#e5e7eb"
            strokeWidth={idx === levelPolygons.length - 1 ? '1.5' : '1'}
            strokeDasharray={idx < levelPolygons.length - 1 ? '2,2' : undefined}
          />
        ))}

        {/* Axis Lines */}
        {axes.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x = center + radius * Math.cos(angle);
          const y = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          );
        })}

        {/* Candidate Score Polygon */}
        <polygon
          points={polygonString}
          fill="url(#radarFill)"
          stroke="#6366f1"
          strokeWidth="2.5"
          className="transition-all duration-700 ease-out"
        />

        {/* Vertex Dots & Labels */}
        {candidatePoints.map((pt, i) => {
          const axis = axes[i];
          const angle = i * angleStep - Math.PI / 2;
          const labelDist = radius + 22;
          const lx = center + labelDist * Math.cos(angle);
          const ly = center + labelDist * Math.sin(angle);

          return (
            <g key={i}>
              <circle
                cx={pt.x}
                cy={pt.y}
                r={4}
                className="fill-indigo-400 stroke-white stroke-2"
              />
              <text
                x={lx}
                y={ly}
                textAnchor="middle"
                dominantBaseline="central"
                className="text-[11px] font-semibold fill-gray-600 select-none"
              >
                {axis.label}
              </text>
              <text
                x={lx}
                y={ly + 12}
                textAnchor="middle"
                dominantBaseline="central"
                className="text-[10px] font-bold fill-indigo-400 select-none"
              >
                {pt.val}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
