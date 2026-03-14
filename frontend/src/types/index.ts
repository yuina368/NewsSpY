export interface Company {
  id: number;
  ticker: string;
  name: string;
  created_at: string;
}

export interface Article {
  id: number;
  company_id: number;
  title: string;
  content: string;
  source: string;
  source_url: string;
  published_at: string;
  sentiment_score: number | null;
  sentiment_confidence: number | null;
  fetched_at: string;
}

export interface Score {
  company: {
    id: number;
    ticker: string;
    name: string;
  };
  score: number;
  article_count: number;
  avg_sentiment: number | null;
  rank: number;
}

export interface NewsSentiment {
  id: number;
  ticker: string;
  published_at: string;
  sentiment_score: number;
  label: string;
  created_at: string;
  url_hash: string;
}

export interface SentimentHistory {
  date: string;
  avg_score: number;
  article_count: number;
  positive_pct: number;
  negative_pct: number;
  neutral_pct: number;
}

export interface TickerSentimentHistoryResponse {
  ticker: string;
  name: string;
  days: number;
  count: number;
  history: SentimentHistory[];
}

export interface DailySentimentsResponse {
  date: string;
  count: number;
  sentiments: DailySentimentItem[];
}

export interface DailySentimentItem {
  ticker: string;
  name: string;
  avg_score: number;
  article_count: number;
  date: string;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
}

export interface ModelStatusResponse {
  loaded: boolean;
  model: string;
  status: string;
}

export interface BatchRunResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface BatchStatusResponse {
  status: 'running' | 'completed' | 'failed';
  step: string;
  progress: number;
  message: string;
  started_at?: string;
  completed_at?: string;
  articles_fetched?: number;
  articles_added?: number;
  articles_analyzed?: number;
  companies_registered?: number;
  scores_saved?: number;
}
