import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { RefreshCw, TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import { Heatmap } from './components/Heatmap';
import { StockDetail } from './components/StockDetail';
import { Search } from './components/Search';
import { apiService } from './services/api';
import type { Company, Score, Article, BatchStatusResponse } from './types';

const COLORS = {
  positive: '#00ff88',
  negative: '#ff3366',
  neutral: '#6b7280',
};

const CHART_COLORS = {
  positive: '#00ff88',
  negative: '#ff3366',
  neutral: '#8884d8',
  grid: 'rgba(0, 255, 255, 0.1)',
  text: '#9ca3af',
};

function App() {
  const [scores, setScores] = useState<Score[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'negative'>('all');
  const [loading, setLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unhealthy' | 'loading'>('loading');
  const [_batchTaskId, setBatchTaskId] = useState<string | null>(null);
  const [batchStatus, setBatchStatus] = useState<BatchStatusResponse | null>(null);
  const [showBatchProgress, setShowBatchProgress] = useState(false);

  useEffect(() => {
    const initializeApp = async () => {
      try {
        setLoading(true);

        // Check health
        const health = await apiService.getHealth();
        setHealthStatus(health.status === 'healthy' ? 'healthy' : 'unhealthy');

        // Load scores for selected date
        await loadScores(selectedDate);
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setHealthStatus('unhealthy');
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
  }, []);

  const loadScores = async (date: string) => {
    try {
      setLoading(true);
      const sentimentParam = sentimentFilter === 'all' ? undefined : sentimentFilter;
      const scoresData = await apiService.getScores(date, { limit: 100, sentiment_filter: sentimentParam });
      setScores(scoresData);

      // Load articles
      const articlesData = await apiService.getArticles({ limit: 20, sentiment_filter: sentimentParam });
      setArticles(articlesData);
    } catch (error) {
      console.error('Failed to load scores:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await loadScores(selectedDate);
  };

  const handleCalculateScores = async () => {
    try {
      setLoading(true);
      await apiService.calculateScores(selectedDate);
      await loadScores(selectedDate);
    } catch (error) {
      console.error('Failed to calculate scores:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateData = async () => {
    try {
      setShowBatchProgress(true);
      const result = await apiService.runBatch();
      setBatchTaskId(result.task_id);
      pollBatchStatus(result.task_id);
    } catch (error) {
      console.error('Failed to start batch processing:', error);
      setShowBatchProgress(false);
    }
  };

  const pollBatchStatus = async (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await apiService.getBatchStatus(taskId);
        setBatchStatus(status);

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          if (status.status === 'completed') {
            await loadScores(selectedDate);
          }
          setTimeout(() => {
            setShowBatchProgress(false);
            setBatchStatus(null);
            setBatchTaskId(null);
          }, 3000);
        }
      } catch (error) {
        console.error('Failed to get batch status:', error);
        clearInterval(interval);
        setShowBatchProgress(false);
      }
    }, 1000);
  };

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
    loadScores(date);
  };

  const handleSentimentFilterChange = (filter: 'all' | 'positive' | 'negative') => {
    setSentimentFilter(filter);
    loadScores(selectedDate);
  };

  const handleStockClick = (ticker: string) => {
    setSelectedStock(ticker);
  };

  const handleCompanySelect = (company: Company) => {
    setSelectedStock(company.ticker);
  };

  const getStats = () => {
    const positiveCount = scores.filter((s) => s.score > 0).length;
    const negativeCount = scores.filter((s) => s.score < 0).length;
    const neutralCount = scores.filter((s) => s.score === 0).length;
    const avgScore = scores.length > 0 ? scores.reduce((sum, s) => sum + s.score, 0) / scores.length : 0;

    return { positiveCount, negativeCount, neutralCount, avgScore };
  };

  const stats = getStats();

  return (
    <div className="min-h-screen animated-gradient grid-pattern">
      {/* Header */}
      <header className="bg-dark-bg/80 backdrop-blur-xl border-b border-dark-border sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Activity className="w-8 h-8 text-neon-cyan" />
                <div className="absolute inset-0 animate-pulse-neon">
                  <Activity className="w-8 h-8 text-neon-cyan opacity-50" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-glow-cyan text-white">NewsSpY</h1>
                <span className="text-xs text-neon-cyan tracking-wider">US STOCK SENTIMENT ANALYSIS</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${healthStatus === 'healthy' ? 'border-neon-green text-neon-green shadow-neon-green' : healthStatus === 'unhealthy' ? 'border-neon-red text-neon-red shadow-neon-red' : 'border-dark-border text-gray-500'}`}>
                <div className={`w-2 h-2 rounded-full ${healthStatus === 'healthy' ? 'bg-neon-green animate-pulse-neon' : healthStatus === 'unhealthy' ? 'bg-neon-red animate-pulse' : 'bg-gray-600'}`} />
                <span className="text-sm font-semibold capitalize">{healthStatus}</span>
              </div>
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-neon-cyan/10 border border-neon-cyan text-neon-cyan rounded-lg hover:bg-neon-cyan hover:text-dark-bg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-neon-cyan"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span className="font-semibold">Refresh</span>
              </button>
              <button
                onClick={handleUpdateData}
                disabled={loading || showBatchProgress}
                className="flex items-center gap-2 px-4 py-2 bg-neon-green/10 border border-neon-green text-neon-green rounded-lg hover:bg-neon-green hover:text-dark-bg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-neon-green"
              >
                <RefreshCw className={`w-4 h-4 ${showBatchProgress ? 'animate-spin' : ''}`} />
                <span className="font-semibold">Update Data</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Controls */}
        <div className="card mb-8 border-pulse">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-neon-cyan mb-2 tracking-wider">DATE</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => handleDateChange(e.target.value)}
                className="input w-full px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-neon-cyan mb-2 tracking-wider">SENTIMENT FILTER</label>
              <select
                value={sentimentFilter}
                onChange={(e) => handleSentimentFilterChange(e.target.value as 'all' | 'positive' | 'negative')}
                className="input w-full px-3 py-2"
              >
                <option value="all">All</option>
                <option value="positive">Positive</option>
                <option value="negative">Negative</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-neon-cyan mb-2 tracking-wider">SEARCH</label>
              <Search onCompanySelect={handleCompanySelect} />
            </div>
          </div>
          <div className="mt-4">
            <button
              onClick={handleCalculateScores}
              disabled={loading}
              className="w-full px-4 py-3 bg-gradient-to-r from-neon-cyan/20 to-neon-magenta/20 border border-neon-cyan text-neon-cyan rounded-lg hover:from-neon-cyan hover:to-neon-magenta hover:text-dark-bg disabled:opacity-50 disabled:cursor-not-allowed font-bold tracking-wider transition-all duration-300 hover:shadow-neon-cyan"
            >
              {loading ? 'CALCULATING...' : 'CALCULATE SCORES'}
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card bg-gradient-to-br from-neon-green/5 to-transparent border-neon-green/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-neon-green tracking-wider font-semibold">POSITIVE</p>
                <p className="text-4xl font-bold text-glow-lime text-neon-green">{stats.positiveCount}</p>
              </div>
              <div className="p-3 bg-neon-green/10 rounded-full">
                <TrendingUp className="w-8 h-8 text-neon-green" />
              </div>
            </div>
          </div>
          <div className="card bg-gradient-to-br from-neon-red/5 to-transparent border-neon-red/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-neon-red tracking-wider font-semibold">NEGATIVE</p>
                <p className="text-4xl font-bold text-glow-red text-neon-red">{stats.negativeCount}</p>
              </div>
              <div className="p-3 bg-neon-red/10 rounded-full">
                <TrendingDown className="w-8 h-8 text-neon-red" />
              </div>
            </div>
          </div>
          <div className="card bg-gradient-to-br from-gray-500/5 to-transparent border-gray-500/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 tracking-wider font-semibold">NEUTRAL</p>
                <p className="text-4xl font-bold text-gray-400">{stats.neutralCount}</p>
              </div>
              <div className="p-3 bg-gray-500/10 rounded-full">
                <Minus className="w-8 h-8 text-gray-400" />
              </div>
            </div>
          </div>
          <div className={`card bg-gradient-to-br ${stats.avgScore > 0 ? 'from-neon-green/5 to-transparent border-neon-green/30' : stats.avgScore < 0 ? 'from-neon-red/5 to-transparent border-neon-red/30' : 'from-gray-500/5 to-transparent border-gray-500/30'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 tracking-wider font-semibold">AVG SCORE</p>
                <p className={`text-4xl font-bold ${stats.avgScore > 0 ? 'text-glow-lime text-neon-green' : stats.avgScore < 0 ? 'text-glow-red text-neon-red' : 'text-gray-400'}`}>
                  {stats.avgScore.toFixed(2)}
                </p>
              </div>
              <div className={`p-3 ${stats.avgScore > 0 ? 'bg-neon-green/10' : stats.avgScore < 0 ? 'bg-neon-red/10' : 'bg-gray-500/10'} rounded-full`}>
                <Activity className={`w-8 h-8 ${stats.avgScore > 0 ? 'text-neon-green' : stats.avgScore < 0 ? 'text-neon-red' : 'text-gray-400'}`} />
              </div>
            </div>
          </div>
        </div>

        {/* Heatmap */}
        <div className="card mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-gradient-to-b from-neon-cyan to-neon-magenta rounded-full"></div>
            <h2 className="text-xl font-bold text-glow-cyan text-white tracking-wider">SENTIMENT HEATMAP</h2>
          </div>
          {scores.length > 0 ? (
            <Heatmap scores={scores} onStockClick={handleStockClick} />
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Activity className="w-16 h-16 mx-auto mb-4 text-neon-cyan/30" />
              <p className="text-neon-cyan/70">No scores available for this date. Click "Calculate Scores" to generate scores.</p>
            </div>
          )}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-1 h-6 bg-neon-cyan rounded-full"></div>
              <h2 className="text-xl font-bold text-white tracking-wider">TOP 10 COMPANIES</h2>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scores.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
                <XAxis dataKey="company.ticker" stroke={CHART_COLORS.text} />
                <YAxis stroke={CHART_COLORS.text} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#12122a', border: '1px solid #00ffff', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend />
                <Bar dataKey="score" fill={CHART_COLORS.positive} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-1 h-6 bg-neon-magenta rounded-full"></div>
              <h2 className="text-xl font-bold text-white tracking-wider">SENTIMENT DISTRIBUTION</h2>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Positive', value: stats.positiveCount },
                    { name: 'Negative', value: stats.negativeCount },
                    { name: 'Neutral', value: stats.neutralCount },
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  dataKey="value"
                >
                  <Cell fill={COLORS.positive} stroke="#0a0a1a" strokeWidth={2} />
                  <Cell fill={COLORS.negative} stroke="#0a0a1a" strokeWidth={2} />
                  <Cell fill={COLORS.neutral} stroke="#0a0a1a" strokeWidth={2} />
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#12122a', border: '1px solid #ff00ff', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Articles */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-6 bg-gradient-to-b from-neon-lime to-neon-cyan rounded-full"></div>
            <h2 className="text-xl font-bold text-white tracking-wider">RECENT ARTICLES</h2>
          </div>
          {articles.length > 0 ? (
            <div className="space-y-4">
              {articles.slice(0, 10).map((article) => (
                <div key={article.id} className="border-b border-dark-border pb-4 last:border-b-0 last:pb-0">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-white mb-1 hover:text-neon-cyan transition-colors cursor-pointer">{article.title}</h3>
                      <p className="text-sm text-gray-400 mb-2">
                        <span className="text-neon-cyan">{article.source}</span> • {new Date(article.published_at).toLocaleDateString('ja-JP')}
                      </p>
                      <p className="text-sm text-gray-500 line-clamp-2">{article.content?.substring(0, 200)}...</p>
                    </div>
                    {article.sentiment_score !== null && (
                      <div className={`ml-4 px-3 py-1 rounded-full font-bold border ${
                        article.sentiment_score > 0
                          ? 'bg-neon-green/10 border-neon-green text-neon-green shadow-neon-green'
                          : article.sentiment_score < 0
                          ? 'bg-neon-red/10 border-neon-red text-neon-red shadow-neon-red'
                          : 'bg-gray-500/10 border-gray-500 text-gray-500'
                      }`}>
                        {article.sentiment_score.toFixed(3)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Activity className="w-16 h-16 mx-auto mb-4 text-neon-cyan/30" />
              <p className="text-neon-cyan/70">No articles available.</p>
            </div>
          )}
        </div>
      </main>

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetail ticker={selectedStock} onClose={() => setSelectedStock(null)} />
      )}

      {/* Batch Progress Modal */}
      {showBatchProgress && batchStatus && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="card max-w-md w-full mx-4 border-neon-cyan border-2 shadow-neon-cyan">
            <div className="flex items-center gap-3 mb-6">
              <RefreshCw className="w-6 h-6 text-neon-cyan animate-spin" />
              <h3 className="text-xl font-bold text-glow-cyan text-white">UPDATING DATA</h3>
            </div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm text-gray-400 mb-2">
                  <span className="text-neon-cyan">{batchStatus.message}</span>
                  <span className="text-neon-magenta font-bold">{batchStatus.progress}%</span>
                </div>
                <div className="w-full bg-dark-bg rounded-full h-3 overflow-hidden border border-dark-border">
                  <div
                    className="h-full rounded-full transition-all duration-300 bg-gradient-to-r from-neon-cyan to-neon-magenta shadow-neon-cyan"
                    style={{ width: `${batchStatus.progress}%` }}
                  />
                </div>
              </div>
              {batchStatus.articles_fetched !== undefined && (
                <div className="text-sm text-gray-400 space-y-1">
                  <p>Articles fetched: <span className="font-semibold text-neon-cyan">{batchStatus.articles_fetched}</span></p>
                  <p>Articles added: <span className="font-semibold text-neon-magenta">{batchStatus.articles_added || 0}</span></p>
                  {batchStatus.articles_analyzed !== undefined && (
                    <p>Articles analyzed: <span className="font-semibold text-neon-green">{batchStatus.articles_analyzed}</span></p>
                  )}
                  {batchStatus.scores_saved !== undefined && (
                    <p>Scores saved: <span className="font-semibold text-neon-lime">{batchStatus.scores_saved}</span></p>
                  )}
                </div>
              )}
              {batchStatus.status === 'completed' && (
                <div className="text-neon-green font-bold text-center text-lg text-glow-lime">
                  ✓ COMPLETED SUCCESSFULLY!
                </div>
              )}
              {batchStatus.status === 'failed' && (
                <div className="text-neon-red font-bold text-center text-lg">
                  ✗ FAILED: {batchStatus.message}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
