import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { X, TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import { apiService } from '../services/api';
import type { TickerSentimentHistoryResponse } from '../types';

interface StockDetailProps {
  ticker: string;
  onClose: () => void;
}

export const StockDetail: React.FC<StockDetailProps> = ({ ticker, onClose }) => {
  const [response, setResponse] = useState<TickerSentimentHistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiService.getTickerSentimentHistory(ticker, 30);
        setResponse(data);
      } catch (err) {
        setError('Failed to fetch sentiment history');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [ticker]);

  const getLatestScore = (): number => {
    if (!response || response.history.length === 0) return 0;
    return response.history[0].avg_score;
  };

  const getScoreIcon = () => {
    const score = getLatestScore();
    if (score > 0.05) return <TrendingUp className="w-8 h-8 text-neon-green" />;
    if (score < -0.05) return <TrendingDown className="w-8 h-8 text-neon-red" />;
    return <Minus className="w-8 h-8 text-gray-400" />;
  };

  const getScoreColor = (): string => {
    const score = getLatestScore();
    if (score > 0.05) return 'text-neon-green text-glow-lime';
    if (score < -0.05) return 'text-neon-red text-glow-red';
    return 'text-gray-400';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="card border-neon-cyan border-2 shadow-neon-cyan max-w-md w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="spinner"></div>
          </div>
          <p className="text-center mt-4 text-neon-cyan font-semibold">Loading sentiment history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="card border-neon-red border-2 shadow-neon-red max-w-md w-full mx-4">
          <Activity className="w-12 h-12 mx-auto text-neon-red mb-4" />
          <p className="text-neon-red text-center font-bold">{error}</p>
          <button
            onClick={onClose}
            className="mt-6 w-full bg-dark-card border border-dark-border text-gray-300 py-2 px-4 rounded-lg hover:bg-dark-border transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="card border-2 border-neon-cyan shadow-neon-cyan max-w-4xl w-full max-h-[90vh] overflow-y-auto scrollbar-neon">
        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-neon-cyan animate-pulse-neon" />
              <h2 className="text-3xl font-bold text-glow-cyan text-white">{response?.name || ticker}</h2>
            </div>
            <p className="text-gray-400 mt-2 text-sm tracking-wider">SENTIMENT HISTORY (LAST {response?.days || 30} DAYS)</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-neon-cyan transition-colors p-2 hover:bg-neon-cyan/10 rounded-lg"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex items-center gap-4 mb-6 p-4 bg-dark-bg/50 rounded-xl border border-dark-border">
          <div className="p-4 bg-gradient-to-br from-neon-cyan/10 to-neon-magenta/10 rounded-full border border-neon-cyan/30">
            {getScoreIcon()}
          </div>
          <div>
            <p className={`text-5xl font-bold ${getScoreColor()}`}>
              {getLatestScore().toFixed(3)}
            </p>
            <p className="text-sm text-gray-400 tracking-wider">LATEST SENTIMENT SCORE</p>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-5 bg-gradient-to-b from-neon-cyan to-neon-magenta rounded-full"></div>
            <h3 className="text-lg font-bold text-white tracking-wider">SENTIMENT TREND</h3>
          </div>
          <div className="bg-dark-bg/50 p-4 rounded-xl border border-dark-border">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={response?.history || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 255, 255, 0.1)" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ja-JP')}
                  stroke="#9ca3af"
                />
                <YAxis
                  domain={[-1, 1]}
                  tickFormatter={(value) => value.toFixed(2)}
                  stroke="#9ca3af"
                />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleDateString('ja-JP')}
                  formatter={(value: number) => [value.toFixed(3), 'Score']}
                  contentStyle={{ backgroundColor: '#12122a', border: '1px solid #00ffff', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="avg_score"
                  stroke="#00ffff"
                  strokeWidth={3}
                  dot={{ fill: '#00ffff', r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#ff00ff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-neon-green/10 to-transparent border border-neon-green/30 p-4 rounded-xl">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-neon-green" />
              <p className="text-xs text-gray-400 tracking-wider">POSITIVE</p>
            </div>
            <p className="text-3xl font-bold text-glow-lime text-neon-green">
              {response && response.history.length > 0 ? `${response.history[0].positive_pct.toFixed(1)}%` : '0%'}
            </p>
          </div>
          <div className="bg-gradient-to-br from-neon-red/10 to-transparent border border-neon-red/30 p-4 rounded-xl">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="w-5 h-5 text-neon-red" />
              <p className="text-xs text-gray-400 tracking-wider">NEGATIVE</p>
            </div>
            <p className="text-3xl font-bold text-glow-red text-neon-red">
              {response && response.history.length > 0 ? `${response.history[0].negative_pct.toFixed(1)}%` : '0%'}
            </p>
          </div>
          <div className="bg-gradient-to-br from-gray-500/10 to-transparent border border-gray-500/30 p-4 rounded-xl">
            <div className="flex items-center gap-2 mb-2">
              <Minus className="w-5 h-5 text-gray-400" />
              <p className="text-xs text-gray-400 tracking-wider">NEUTRAL</p>
            </div>
            <p className="text-3xl font-bold text-gray-400">
              {response && response.history.length > 0 ? `${response.history[0].neutral_pct.toFixed(1)}%` : '0%'}
            </p>
          </div>
        </div>

        <div className="mt-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-5 bg-neon-magenta rounded-full"></div>
            <h3 className="text-lg font-bold text-white tracking-wider">DAILY SENTIMENT HISTORY</h3>
          </div>
          <div className="space-y-2">
            {(response?.history || []).slice(0, 5).map((item, index) => (
              <div key={index} className="bg-dark-bg/50 p-4 rounded-xl border border-dark-border hover:border-neon-cyan/50 transition-colors">
                <div className="flex justify-between items-center">
                  <p className="text-sm font-semibold text-gray-300">{new Date(item.date).toLocaleDateString('ja-JP')}</p>
                  <p className={`text-sm font-bold ${
                    item.avg_score > 0
                      ? 'text-neon-green text-glow-lime'
                      : item.avg_score < 0
                      ? 'text-neon-red text-glow-red'
                      : 'text-gray-400'
                  }`}>
                    {item.avg_score.toFixed(3)}
                  </p>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Activity className="w-4 h-4 text-neon-cyan" />
                  <p className="text-xs text-gray-500">{item.article_count} articles analyzed</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
