interface HeatmapProps {
  scores: Array<{
    company: { ticker: string; name: string };
    score: number;
    article_count: number;
  }>;
  onStockClick: (ticker: string) => void;
}

export const Heatmap = ({ scores, onStockClick }: HeatmapProps) => {
  const getScoreGradient = (score: number): string => {
    if (score > 0.2) return 'bg-gradient-to-br from-neon-green to-emerald-600 shadow-neon-green';
    if (score > 0.1) return 'bg-gradient-to-br from-neon-lime/80 to-green-500';
    if (score > 0) return 'bg-gradient-to-br from-green-400/60 to-green-600/60';
    if (score === 0) return 'bg-gradient-to-br from-gray-500/40 to-gray-600/40';
    if (score > -0.1) return 'bg-gradient-to-br from-red-400/60 to-red-600/60';
    if (score > -0.2) return 'bg-gradient-to-br from-orange-500/80 to-red-500';
    return 'bg-gradient-to-br from-neon-red to-red-700 shadow-neon-red';
  };

  const getScoreTextColor = (score: number): string => {
    return Math.abs(score) > 0.15 ? 'text-white font-bold' : 'text-gray-900 font-semibold';
  };

  const getBorderColor = (score: number): string => {
    if (score > 0.1) return 'border-neon-green';
    if (score < -0.1) return 'border-neon-red';
    return 'border-dark-border';
  };

  return (
    <div className="grid grid-cols-10 gap-1">
      {scores.map((item, index) => (
        <div
          key={index}
          className={`
            ${getScoreGradient(item.score)}
            ${getScoreTextColor(item.score)}
            ${getBorderColor(item.score)}
            border p-2 rounded-lg cursor-pointer hover:scale-105 hover:z-10
            transition-all duration-300 min-h-[70px] flex flex-col
            justify-center items-center relative overflow-hidden group
          `}
          onClick={() => onStockClick(item.company.ticker)}
          title={`${item.company.ticker}: ${item.company.name}\nScore: ${item.score.toFixed(3)}\nArticles: ${item.article_count}`}
        >
          {/* Glow effect on hover */}
          <div className="absolute inset-0 bg-white/0 group-hover:bg-white/10 transition-all duration-300 rounded-lg" />
          <div className="relative z-10">
            <div className="font-bold text-sm tracking-wider">{item.company.ticker}</div>
            <div className="text-xs mt-1">{item.score.toFixed(2)}</div>
          </div>
          {/* Corner accent */}
          <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/30 rounded-tr-sm" />
          <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/30 rounded-bl-sm" />
        </div>
      ))}
    </div>
  );
};
