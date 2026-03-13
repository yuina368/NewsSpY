# NewsSpY - US Stock Sentiment Analysis Dashboard

**[日本語](#japanese) | [English](#english) | [中文](#chinese)**

---

<a name="japanese"></a>
# 🇯🇵 日本語

# NewsSpY - US Stock Sentiment Analysis Dashboard

米国株（NYSE主要銘柄）のニュースを自動取得し、FinBERT AIモデルを用いて感情解析を行い、そのスコアを可視化するWebアプリケーションです。

## 🚀 特徴

- **自動ニュース収集**: GNews API（無料）およびyfinanceから毎日自動的にニュースを収集
- **複数銘柄一括取得**: 1回のAPIリクエストで複数銘柄のニュースをまとめて取得（効率化）
- **自動記事分類**: キーワードマッチングで各記事を適切な銘柄に自動分類
- **AI感情解析**: 金融特化型AIモデル「FinBERT」を用いて感情解析（ポジティブ/ネガティブ/ニュートラル）を実行
- **日本時間フィルタリング**: JST 6:00-22:00のニュースのみを解析（米国市場開始前のニュースに焦点）
- **感情ヒートマップ**: 各銘柄の感情スコアをタイル状に可視化
- **銘柄詳細**: 特定銘柄の感情スコアの時系列推移を折れ線グラフで表示
- **検索機能**: 44社のリストから銘柄を検索
- **リアルタイム更新**: 最新のニュースと感情スコアをリアルタイムで反映

## 🛠 技術スタック

### Backend
- **FastAPI**: 高性能なPython Webフレームワーク
- **Python 3.10+**: メインプログラミング言語
- **FinBERT (ProsusAI/finbert)**: 金融特化型AI感情解析モデル
- **SQLite**: データベース（WALモードで並行処理対応）
- **GNews API**: ニュースデータソース（無料プラン: 100リクエスト/日）
- **yfinance**: Yahoo Financeからのニュース取得

### Frontend
- **React 18**: UIフレームワーク
- **Vite**: 高速なビルドツール
- **TypeScript**: 型安全なJavaScript
- **Tailwind CSS**: ユーティリティファーストのCSSフレームワーク
- **Recharts**: インタラクティブなデータ可視化ライブラリ
- **Axios**: HTTPクライアント

### Infrastructure
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナ管理
- **Nginx**: リバースプロキシ

## 📁 プロジェクト構造

```
newspy/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPIアプリケーションエントリーポイント
│   │   ├── config.py               # 設定ファイル
│   │   ├── database.py             # データベース操作
│   │   ├── routes/
│   │   │   ├── auth.py            # 認証API
│   │   │   ├── sentiments.py      # 感情スコアAPI
│   │   │   ├── scores.py          # スコアAPI
│   │   │   └── articles.py        # 記事API
│   │   └── services/
│   │       ├── auth.py            # 認証サービス
│   │       └── sentiment_analyzer.py  # FinBERT感情分析
│   ├── batch/
│   │   ├── main.py                 # バッチ処理メイン
│   │   └── news_fetcher.py         # GNews/yfinance連携（複数銘柄一括取得）
│   ├── companies.json              # 企業マスタ（44銘柄）
│   ├── requirements.txt            # Python依存関係
│   └── Dockerfile                  # Dockerイメージ
├── frontend/
│   ├── src/
│   │   ├── main.tsx               # Reactエントリーポイント
│   │   ├── App.tsx                # メインアプリケーション
│   │   ├── index.css              # グローバルスタイル
│   │   ├── components/
│   │   │   ├── Heatmap.tsx        # 感情ヒートマップ
│   │   │   ├── Search.tsx         # 検索機能
│   │   │   └── StockDetail.tsx    # 銘柄詳細
│   │   ├── services/
│   │   │   └── api.ts             # APIクライアント
│   │   └── types/
│   │       └── index.ts           # TypeScript型定義
│   ├── package.json               # Node.js依存関係
│   ├── vite.config.ts             # Vite設定
│   ├── tailwind.config.js         # Tailwind CSS設定
│   └── Dockerfile                 # Dockerイメージ
├── nginx/
│   └── nginx.conf                 # Nginxリバースプロキシ設定
├── docker-compose.yml             # Docker Compose設定
├── .env.example                   # 環境変数テンプレート
└── README.md                      # プロジェクトドキュメント
```

## 🚀 クイックスタート

### 前提条件

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 1. GNews APIキーの取得（無料）

1. [GNews](https://gnews.io/) にアクセス
2. 「Get API Key」をクリック
3. Googleアカウントでサインアップ
4. ダッシュボードからAPIキーをコピー

| プラン | 価格 | リクエスト数 |
|--------|------|-------------|
| Free | 無料 | 100リクエスト/日 |
| Basic | $15/月 | 1,000リクエスト/日 |

### 2. リポジトリのクローン

```bash
git clone <repository-url>
cd NewsSpY
```

### 3. 環境変数の設定

```bash
cp .env.example .env
nano .env
```

`.env`ファイルにAPIキーを設定：

```bash
# GNews API（無料）
GNEWS_API_KEY=your-gnews-api-key-here

# データベース
DATABASE_URL=/app/data/newspy.db
```

### 4. Dockerコンテナの起動

```bash
docker-compose up -d
```

### 5. バッチ処理の実行（ニュース取得＆感情解析）

```bash
docker exec newspy-backend python -m batch.main
```

### 6. アクセス

- **ダッシュボード**: http://localhost
- **APIドキュメント**: http://localhost/api/docs

---

## 📊 対象銘柄（44社）

### テクノロジー
- AAPL（Apple）、MSFT（Microsoft）、GOOGL（Alphabet）、AMZN（Amazon）
- TSLA（Tesla）、META（Meta）、NVDA（NVIDIA）、NFLX（Netflix）
- CRM（Salesforce）、ADOBE（Adobe）

### 金融
- JPM（JPMorgan Chase）、BAC（Bank of America）、WFC（Wells Fargo）
- GS（Goldman Sachs）、MS（Morgan Stanley）、BLK（BlackRock）
- ICE（Intercontinental Exchange）、CME（CME Group）
- V（Visa）、MA（Mastercard）、AXP（American Express）

### ヘルスケア
- JNJ（Johnson & Johnson）、UNH（UnitedHealth）、PFE（Pfizer）
- ABBV（AbbVie）、MRK（Merck）、TMO（Thermo Fisher）、LLY（Eli Lilly）

### 消費財・一般
- WMT（Walmart）、KO（Coca-Cola）、PEP（PepsiCo）、COST（Costco）
- MCD（McDonald's）、NKE（Nike）、LOW（Lowe's）

### エネルギー・産業
- XOM（Exxon Mobil）、CVX（Chevron）、BA（Boeing）
- HON（Honeywell）、GE（General Electric）

### 通信・メディア
- VZ（Verizon）、T（AT&T）、CMCSA（Comcast）、DIS（Disney）

---

## ⏰ 時刻フィルタリングについて

**JST 6:00-22:00 のニュースのみを解析対象とします**

- 日本時間6時〜22時は、米国市場が開く前の時間帯
- 市場開始前のニュースは、その日の取引に大きな影響を与える
- 22時以降（米国市場終了後）のニュースは翌日扱い

---

## 🔧 開発

### バックエンド開発

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m batch.main  # バッチ処理実行
```

### フロントエンド開発

```bash
cd frontend
npm install
npm run dev
```

---

## 📝 APIドキュメント

### エンドポイント

| エンドポイント | 説明 |
|----------------|------|
| `GET /api/companies/` | 全企業リスト取得 |
| `GET /api/scores/ranking/{date}` | 指定日のランキング取得 |
| `GET /api/scores/{ticker}` | 銘柄別スコア時系列取得 |
| `GET /api/articles/?ticker={ticker}` | 銘柄別ニュース記事取得 |
| `GET /api/sentiments/{ticker}` | 銘柄別感情スコア取得 |

詳細は http://localhost/api/docs を参照

---

## 🔄 定期実行の設定

### Cron設定（毎日日本時間22時に実行）

```bash
crontab -e
```

```cron
0 22 * * * cd /home/yuina/NewsSpY && docker exec newspy-backend python -m batch.main
```

---

## 📄 ライセンス

MIT License

---

## 🙏 参考文献

- [FinBERT](https://huggingface.co/ProsusAI/finbert) - 金融感情分析モデル
- [GNews API](https://gnews.io/) - ニュースデータソース
- [yfinance](https://pypi.org/project/yfinance/) - Yahoo Finance API

---

<a name="english"></a>
# 🇺🇸 English

# NewsSpY - US Stock Sentiment Analysis Dashboard

A web application that automatically collects news about US stocks (NYSE major companies), performs sentiment analysis using the FinBERT AI model, and visualizes the scores.

## 🚀 Features

- **Automatic News Collection**: Daily collection from GNews API (free tier) and yfinance
- **Batch Multi-Ticker Fetch**: Fetch news for multiple tickers in a single API request
- **Auto Article Classification**: Automatically classify articles to relevant tickers using keyword matching
- **AI Sentiment Analysis**: Financial-specific AI model "FinBERT" for sentiment analysis
- **JST Time Filter**: Only analyze news published during JST 6:00-22:00 (pre-US market hours)
- **Sentiment Heatmap**: Visualize sentiment scores across companies
- **Stock Detail**: Time-series sentiment score charts for individual stocks
- **Search**: Search across 44 companies
- **Real-time Updates**: Reflect latest news and sentiment scores

## 🛠 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Python 3.10+**
- **FinBERT (ProsusAI/finbert)**: Financial-specific AI sentiment analysis
- **SQLite**: Database with WAL mode
- **GNews API**: News source (Free: 100 requests/day)
- **yfinance**: Yahoo Finance news fetching

### Frontend
- **React 18** with **Vite**
- **TypeScript**
- **Tailwind CSS**
- **Recharts** for data visualization

### Infrastructure
- **Docker** & **Docker Compose**
- **Nginx** reverse proxy

## 🚀 Quick Start

### 1. Get GNews API Key (Free)

1. Visit [GNews](https://gnews.io/)
2. Click "Get API Key"
3. Sign up with Google account
4. Copy API key from dashboard

### 2. Clone & Setup

```bash
git clone <repository-url>
cd NewsSpY
cp .env.example .env
# Edit .env and add GNEWS_API_KEY
docker-compose up -d
```

### 3. Run Batch Processing

```bash
docker exec newspy-backend python -m batch.main
```

### 4. Access

- **Dashboard**: http://localhost
- **API Docs**: http://localhost/api/docs

---

## 📊 Tracked Companies (44)

### Technology
- AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, NFLX, CRM, ADOBE

### Financials
- JPM, BAC, WFC, GS, MS, BLK, ICE, CME, V, MA, AXP

### Healthcare
- JNJ, UNH, PFE, ABBV, MRK, TMO, LLY

### Consumer
- WMT, KO, PEP, COST, MCD, NKE, LOW

### Energy/Industrial
- XOM, CVX, BA, HON, GE

### Telecom/Media
- VZ, T, CMCSA, DIS

---

## ⏰ Time Filtering

**Only news published during JST 6:00-22:00 is analyzed**

- JST 6:00-22:00 corresponds to pre-US market hours
- News before market opening significantly impacts trading
- News after 22:00 JST (post-US market close) is treated as next day

---

## 📝 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/companies/` | List all companies |
| `GET /api/scores/ranking/{date}` | Get ranking by date |
| `GET /api/scores/{ticker}` | Get ticker score time-series |
| `GET /api/articles/?ticker={ticker}` | Get news by ticker |
| `GET /api/sentiments/{ticker}` | Get sentiment by ticker |

Full docs: http://localhost/api/docs

---

## 🔄 Cron Setup

```bash
crontab -e
```

```cron
0 22 * * * cd /home/yuina/NewsSpY && docker exec newspy-backend python -m batch.main
```

---

## 📄 License

MIT License

---

## 🙏 References

- [FinBERT](https://huggingface.co/ProsusAI/finbert)
- [GNews API](https://gnews.io/)
- [yfinance](https://pypi.org/project/yfinance/)

---

<a name="chinese"></a>
# 🇨🇳 中文

# NewsSpY - 美股情绪分析仪表板

自动收集美股（NYSE主要公司）新闻，使用 FinBERT AI 模型进行情绪分析，并可视化评分的 Web 应用程序。

## 🚀 特性

- **自动新闻收集**: 每日从 GNews API（免费）和 yfinance 收集
- **批量多股票获取**: 单次 API 请求获取多个股票的新闻
- **自动文章分类**: 使用关键词匹配自动分类文章
- **AI 情绪分析**: 金融专用 AI 模型 "FinBERT" 进行情绪分析
- **JST 时间过滤**: 仅分析 JST 6:00-22:00 发布的新闻（美股开盘前）
- **情绪热力图**: 可视化各公司情绪评分
- **股票详情**: 个别股票的情绪评分时序图
- **搜索**: 搜索 44 家公司
- **实时更新**: 反映最新新闻和情绪评分

## 🚀 快速开始

### 1. 获取 GNews API 密钥（免费）

1. 访问 [GNews](https://gnews.io/)
2. 点击 "Get API Key"
3. 使用 Google 账号注册
4. 从仪表板复制 API 密钥

### 2. 克隆和设置

```bash
git clone <repository-url>
cd NewsSpY
cp .env.example .env
# 编辑 .env 添加 GNEWS_API_KEY
docker-compose up -d
```

### 3. 运行批处理

```bash
docker exec newspy-backend python -m batch.main
```

### 4. 访问

- **仪表板**: http://localhost
- **API 文档**: http://localhost/api/docs

---

## 📊 追踪公司（44家）

### 科技
- AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, NFLX, CRM, ADOBE

### 金融
- JPM, BAC, WFC, GS, MS, BLK, ICE, CME, V, MA, AXP

### 医疗保健
- JNJ, UNH, PFE, ABBV, MRK, TMO, LLY

### 消费品
- WMT, KO, PEP, COST, MCD, NKE, LOW

### 能源/工业
- XOM, CVX, BA, HON, GE

### 通信/媒体
- VZ, T, CMCSA, DIS

---

## ⏰ 时间过滤

**仅分析 JST 6:00-22:00 发布的新闻**

- JST 6:00-22:00 对应美股开盘前时间
- 开盘前的新闻对交易影响重大
- 22:00 JST 之后（美股收盘后）的新闻视为次日

---

## 📝 API 端点

| 端点 | 描述 |
|------|------|
| `GET /api/companies/` | 列出所有公司 |
| `GET /api/scores/ranking/{date}` | 按日期获取排名 |
| `GET /api/scores/{ticker}` | 获取股票评分时序 |
| `GET /api/articles/?ticker={ticker}` | 按股票获取新闻 |
| `GET /api/sentiments/{ticker}` | 按股票获取情绪 |

完整文档: http://localhost/api/docs

---

## 📄 许可证

MIT License
