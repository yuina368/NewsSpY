# NewsSpY - US Stock Sentiment Analysis Dashboard

**[日本語](#japanese) | [English](#english) | [中文](#chinese)**

---

<a name="japanese"></a>
# 🇯🇵 日本語

# NewsSpY - US Stock Sentiment Analysis Dashboard

米国株（S&P 500相当）のニュースを自動取得し、FinBERT AIモデルを用いて感情解析を行い、そのスコアを可視化するWebアプリケーションです。

## 🚀 特徴

- **自動ニュース収集**: NewsAPIおよびyfinanceから毎日自動的にニュースを収集
- **AI感情解析**: 金融特化型AIモデル「FinBERT」を用いて感情解析（ポジティブ/ネガティブ/ニュートラル）を実行
- **感情ヒートマップ**: S&P 500の各銘柄の感情スコアをタイル状に可視化
- **銘柄詳細**: 特定銘柄の感情スコアの時系列推移を折れ線グラフで表示
- **検索機能**: 500社のリストから銘柄を検索
- **リアルタイム更新**: 最新のニュースと感情スコアをリアルタイムで反映

## 🛠 技術スタック

### Backend
- **FastAPI**: 高性能なPython Webフレームワーク
- **Python 3.10+**: メインプログラミング言語
- **FinBERT**: 金融特化型AI感情解析モデル（Hugging Face Transformers）
- **SQLite**: データベース（初期フェーズ）
- **NewsAPI**: ニュースデータソース
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
│   │   │   ├── scores.py         # スコアAPI
│   │   │   └── articles.py       # 記事API
│   │   └── services/
│   │       ├── auth.py            # 認証サービス
│   │       ├── sentiment_analyzer.py  # FinBERT感情分析
│   │       └── score_calculator.py    # スコア計算
│   ├── batch/
│   │   ├── main.py                 # バッチ処理メイン
│   │   └── news_fetcher.py         # NewsAPI連携
│   ├── companies.json              # 企業マスタ
│   ├── requirements.txt            # Python依存関係
│   └── Dockerfile                # Dockerイメージ
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
│   └── nginx.conf                # Nginxリバースプロキシ設定
├── docker-compose.yml             # Docker Compose設定
├── .env.example                 # 環境変数テンプレート
└── README.md                    # プロジェクトドキュメント
```

## 🚀 クイックスタート

### 前提条件

- Docker 20.10+ （[インストールガイド](DOCKER_INSTALL.md)を参照）
- Docker Compose 2.0+ （またはローカル開発環境）
- Git

> **💡 Dockerがインストールされていない場合**: [Dockerインストールガイド](DOCKER_INSTALL.md)を参照してください。

### インストール

#### 方法1: シェルスクリプトを使用（最も簡単）

**⚡ ワンコマンドで起動:**

```bash
./start_server.sh
```

このスクリプトは以下の処理を自動的に行います：
- 既存のコンテナの停止・削除
- 未使用のDockerリソースのクリーンアップ
- Docker Composeでのサーバー起動
- ヘルスチェックと起動確認

**📱 アプリケーションにアクセス:**
- Frontend: http://localhost:3000
- Main: http://localhost
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

---

#### 方法2: Docker Composeを使用（推奨）

1. リポジトリをクローン
```bash
git clone <repository-url>
cd newspy
```

2. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集してNewsAPIキーを設定
```

3. Docker Composeで起動
```bash
docker-compose up -d
```

4. アプリケーションにアクセス
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

#### 方法2: ローカル開発（Dockerなし）

Docker Composeがインストールされていない場合、ローカルで開発できます。

##### Backendの起動

```bash
cd backend

# 仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# データベースを初期化
python -c "from app.database import init_database; init_database()"

# サーバーを起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

##### Frontendの起動（React + Vite）

```bash
cd frontend

# Node.js依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

##### アプリケーションにアクセス
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

#### Docker Composeのインストール

Docker Composeをインストールするには、以下のコマンドを実行してください：

**Linux:**
```bash
# 最新バージョンをダウンロード
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 実行権限を付与
sudo chmod +x /usr/local/bin/docker-compose

# バージョンを確認
docker-compose --version
```

**Mac (Homebrewを使用):**
```bash
brew install docker-compose
```

**Windows:**
Docker Desktopをインストールすると、Docker Composeも含まれています。
https://www.docker.com/products/docker-desktop/

## 📊 APIエンドポイント

### 認証API

#### ログイン（トークン取得）
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

#### 現在のユーザー情報取得
```
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### トークン更新
```
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

### 感情スコアAPI

#### 日次感情スコア取得（ヒートマップ用）
```
GET /api/sentiments/daily?target_date=YYYY-MM-DD
```

#### 銘柄別感情履歴取得（チャート用）
```
GET /api/sentiments/{ticker}?days=30
```

#### 感情サマリー取得
```
GET /api/sentiments/summary
```

### その他API

#### ヘルスチェック
```
GET /api/health/
```

#### モデルステータス
```
GET /api/model/status
```

詳細なAPIドキュメントは、[http://localhost/api/docs](http://localhost/api/docs) で確認できます。

## 🖥️ サーバー管理

### サーバーの起動

**⚡ シェルスクリプトを使用（推奨）:**
```bash
./start_server.sh
```

**🔧 Docker Composeを使用:**
```bash
docker-compose up -d
```

### サーバーの停止

```bash
docker-compose down
```

### サーバーの再起動

```bash
docker-compose restart
```

### サーバーのステータス確認

```bash
docker-compose ps
```

### ログの確認

```bash
# すべてのログ
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### コンテナの再ビルド

```bash
# キャッシュなしで再ビルド
docker-compose build --no-cache

# 特定のサービスのみ再ビルド
docker-compose build backend
docker-compose build frontend

# 再ビルドして起動
docker-compose up -d --build
```

## � バッチ処理

バッチ処理は以下の手順で実行されます：

1. **データベース初期化**: テーブルを作成
2. **企業登録**: companies.jsonから企業を登録
3. **ニュース取得**: NewsAPIから過去24時間のニュースを取得
4. **キーワードフィルタリング**: 企業名とキーワードでニュースをフィルタリング
5. **感情解析**: FinBERTで感情解析を実行
6. **データ保存**: 解析結果をデータベースに保存

### 手動実行

#### Docker環境の場合

```bash
# Dockerコンテナ内で実行
docker-compose exec backend python batch/main.py
```

#### ローカル環境の場合

```bash
# バッチ処理スクリプトを使用（推奨）
cd backend
bash run_batch.sh

# または直接実行
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python batch/main.py
```

### 自動実行（cron）

cronを使用して定期的にバッチ処理を実行できます：

```bash
# 毎日午前9時に実行（Docker環境）
0 9 * * * cd /app && python batch/main.py

# 毎日午前9時に実行（ローカル環境）
0 9 * * * cd /path/to/backend && bash run_batch.sh
```

## 🎨 データ構造

### 企業マスタ (companies.json)

```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "keywords": ["Apple", "iPhone", "iPad", "Mac", "iOS", "Tim Cook"]
  }
]
```

### データベーステーブル

#### news_sentimentsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| ticker | TEXT | 銘柄コード（Indexed） |
| published_at | TIMESTAMP | ニュース公開日時 |
| sentiment_score | REAL | FinBERTのスコア（-1.0 to 1.0） |
| label | TEXT | positive / negative / neutral |
| created_at | TIMESTAMP | レコード作成日 |
| url_hash | TEXT | ニュースURLのハッシュ（ユニーク制約） |

## 🔧 設定

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|----------|------|------------|
| NEWSAPI_KEY | NewsAPIのAPIキー | demo |
| DATABASE_URL | データベースのパス | newspy.db |
| JWT_SECRET_KEY | JWTトークンの署名キー | your-secret-key-change-this-in-production |
| ACCESS_TOKEN_EXPIRE_MINUTES | アクセストークンの有効期限（分） | 60 |
| ALLOWED_ORIGINS | 許可するオリジン（カンマ区切り） | http://localhost:3000 |

### NewsAPIキーの取得

1. [NewsAPI](https://newsapi.org/) にアカウント登録
2. APIキーを取得
3. `.env`ファイルに設定

## 📝 開発

### クイックスタート（開発）

```bash
# サーバーを起動
./start_server.sh

# または手動で起動
docker-compose up -d
```

### Backend開発

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend開発

```bash
cd frontend
npm install
npm run dev
```

### テスト

```bash
# Backendテスト
cd backend
pytest

# Frontendテスト
cd frontend
npm test
```

## 🐛 トラブルシューティング

### サーバーが起動しない

**シェルスクリプトを使用する場合:**
```bash
# スクリプトを実行
./start_server.sh
```

**手動で起動する場合:**
```bash
# 既存のコンテナを停止・削除
docker-compose down

# 未使用のDockerリソースをクリーンアップ
docker system prune -f

# サーバーを起動
docker-compose up -d

# ステータスを確認
docker-compose ps

# ログを確認
docker-compose logs -f
```

### FinBERTモデルが読み込めない

```bash
# モデルキャッシュをクリア
rm -rf ~/.cache/huggingface

# 再インストール
pip install --upgrade transformers torch
```

### NewsAPIの制限に達した

無料枠の制限を考慮し、以下の対策を実装しています：
- 1リクエストで可能な限り多くの情報を取得
- yfinanceをフォールバックとして使用
- デモデータを提供

### Dockerコンテナが起動しない

```bash
# コンテナログを確認
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# 再ビルド
docker-compose build --no-cache
docker-compose up -d
```

### ポートが既に使用されている

```bash
# ポートを使用しているプロセスを確認
lsof -i :8000
lsof -i :3000
lsof -i :80

# プロセスを強制終了
kill -9 <PID>
```

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエストを歓迎します！

## 📧 お問い合わせ

問題やご質問がある場合は、Issueを開いてください。

## 🙏 謝辞

- [FinBERT](https://huggingface.co/ProsusAI/finbert) - 感情解析モデル
- [NewsAPI](https://newsapi.org/) - ニュースデータ
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Financeデータ
- [FastAPI](https://fastapi.tiangolo.com/) - Webフレームワーク
- [React](https://reactjs.org/) - UIフレームワーク

---

**NewsSpY © 2026 | US Stock Sentiment Analysis Dashboard**

---

<a name="english"></a>
# 🇺🇸 English

# NewsSpY - US Stock Sentiment Analysis Dashboard

A web application that automatically fetches news for US stocks (S&P 500 equivalent), performs sentiment analysis using the FinBERT AI model, and visualizes the scores.

## 🚀 Features

- **Automated News Collection**: Automatically collects news daily from NewsAPI and yfinance
- **AI Sentiment Analysis**: Analyzes sentiment (positive/negative/neutral) using "FinBERT", a finance-specialized AI model
- **Sentiment Heatmap**: Visualizes sentiment scores for each S&P 500 ticker in a tile layout
- **Stock Detail**: Displays time-series sentiment score trends for specific tickers as line charts
- **Search**: Search tickers from a list of 500 companies
- **Real-time Updates**: Reflects the latest news and sentiment scores in real time

## 🛠 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Python 3.10+**: Main programming language
- **FinBERT**: Finance-specialized AI sentiment analysis model (Hugging Face Transformers)
- **SQLite**: Database (initial phase)
- **NewsAPI**: News data source
- **yfinance**: News retrieval from Yahoo Finance

### Frontend
- **React 18**: UI framework
- **Vite**: Fast build tool
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Interactive data visualization library
- **Axios**: HTTP client

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container management
- **Nginx**: Reverse proxy

## 📁 Project Structure

```
newspy/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database operations
│   │   ├── routes/
│   │   │   ├── auth.py            # Auth API
│   │   │   ├── sentiments.py      # Sentiment score API
│   │   │   ├── scores.py         # Score API
│   │   │   └── articles.py       # Articles API
│   │   └── services/
│   │       ├── auth.py            # Auth service
│   │       ├── sentiment_analyzer.py  # FinBERT sentiment analysis
│   │       └── score_calculator.py    # Score calculation
│   ├── batch/
│   │   ├── main.py                 # Batch processing main
│   │   └── news_fetcher.py         # NewsAPI integration
│   ├── companies.json              # Company master data
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                # Docker image
├── frontend/
│   ├── src/
│   │   ├── main.tsx               # React entry point
│   │   ├── App.tsx                # Main application
│   │   ├── index.css              # Global styles
│   │   ├── components/
│   │   │   ├── Heatmap.tsx        # Sentiment heatmap
│   │   │   ├── Search.tsx         # Search feature
│   │   │   └── StockDetail.tsx    # Stock detail
│   │   ├── services/
│   │   │   └── api.ts             # API client
│   │   └── types/
│   │       └── index.ts           # TypeScript type definitions
│   ├── package.json               # Node.js dependencies
│   ├── vite.config.ts             # Vite configuration
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   └── Dockerfile                 # Docker image
├── nginx/
│   └── nginx.conf                # Nginx reverse proxy configuration
├── docker-compose.yml             # Docker Compose configuration
├── .env.example                 # Environment variable template
└── README.md                    # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ (see [Installation Guide](DOCKER_INSTALL.md))
- Docker Compose 2.0+ (or local development environment)
- Git

> **💡 If Docker is not installed**: See [Docker Installation Guide](DOCKER_INSTALL.md).

### Installation

#### Option 1: Using Shell Script (Easiest)

**⚡ One-command launch:**

```bash
./start_server.sh
```

This script automatically:
- Stops and removes existing containers
- Cleans up unused Docker resources
- Starts the server with Docker Compose
- Runs health checks and confirms startup

**📱 Access the application:**
- Frontend: http://localhost:3000
- Main: http://localhost
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

---

#### Option 2: Using Docker Compose (Recommended)

1. Clone the repository
```bash
git clone <repository-url>
cd newspy
```

2. Set environment variables
```bash
cp .env.example .env
# Edit .env and set your NewsAPI key
```

3. Start with Docker Compose
```bash
docker-compose up -d
```

4. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

#### Option 3: Local Development (Without Docker)

If Docker Compose is not installed, you can run locally.

##### Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.database import init_database; init_database()"

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

##### Start Frontend (React + Vite)

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

##### Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health/

#### Installing Docker Compose

**Linux:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

**Mac (via Homebrew):**
```bash
brew install docker-compose
```

**Windows:**
Install Docker Desktop, which includes Docker Compose.
https://www.docker.com/products/docker-desktop/

## 📊 API Endpoints

### Auth API

#### Login (Get Token)
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

#### Get Current User Info
```
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### Refresh Token
```
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

### Sentiment Score API

#### Get Daily Sentiment Scores (for Heatmap)
```
GET /api/sentiments/daily?target_date=YYYY-MM-DD
```

#### Get Sentiment History by Ticker (for Chart)
```
GET /api/sentiments/{ticker}?days=30
```

#### Get Sentiment Summary
```
GET /api/sentiments/summary
```

### Other APIs

#### Health Check
```
GET /api/health/
```

#### Model Status
```
GET /api/model/status
```

Full API documentation available at [http://localhost/api/docs](http://localhost/api/docs).

## 🖥️ Server Management

### Start Server

**⚡ Using shell script (recommended):**
```bash
./start_server.sh
```

**🔧 Using Docker Compose:**
```bash
docker-compose up -d
```

### Stop Server
```bash
docker-compose down
```

### Restart Server
```bash
docker-compose restart
```

### Check Server Status
```bash
docker-compose ps
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Rebuild Containers
```bash
# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Rebuild and start
docker-compose up -d --build
```

## 🔄 Batch Processing

Batch processing runs in the following steps:

1. **Database Initialization**: Create tables
2. **Company Registration**: Register companies from companies.json
3. **News Fetching**: Retrieve last 24 hours of news from NewsAPI
4. **Keyword Filtering**: Filter news by company name and keywords
5. **Sentiment Analysis**: Run FinBERT sentiment analysis
6. **Data Storage**: Save analysis results to database

### Manual Execution

#### Docker environment
```bash
docker-compose exec backend python batch/main.py
```

#### Local environment
```bash
cd backend
bash run_batch.sh

# Or directly
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python batch/main.py
```

### Scheduled Execution (cron)
```bash
# Run daily at 9 AM (Docker)
0 9 * * * cd /app && python batch/main.py

# Run daily at 9 AM (local)
0 9 * * * cd /path/to/backend && bash run_batch.sh
```

## 🎨 Data Structure

### Company Master (companies.json)

```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "keywords": ["Apple", "iPhone", "iPad", "Mac", "iOS", "Tim Cook"]
  }
]
```

### Database Tables

#### news_sentiments table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| ticker | TEXT | Ticker symbol (Indexed) |
| published_at | TIMESTAMP | News publication date/time |
| sentiment_score | REAL | FinBERT score (-1.0 to 1.0) |
| label | TEXT | positive / negative / neutral |
| created_at | TIMESTAMP | Record creation date |
| url_hash | TEXT | News URL hash (unique constraint) |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| NEWSAPI_KEY | NewsAPI key | demo |
| DATABASE_URL | Database path | newspy.db |
| JWT_SECRET_KEY | JWT token signing key | your-secret-key-change-this-in-production |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiry (minutes) | 60 |
| ALLOWED_ORIGINS | Allowed origins (comma-separated) | http://localhost:3000 |

### Getting a NewsAPI Key

1. Register at [NewsAPI](https://newsapi.org/)
2. Get your API key
3. Set it in `.env`

## 📝 Development

### Quick Start (Development)
```bash
./start_server.sh

# Or manually
docker-compose up -d
```

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🐛 Troubleshooting

### Server won't start

**Using shell script:**
```bash
./start_server.sh
```

**Manual start:**
```bash
docker-compose down
docker system prune -f
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

### FinBERT model fails to load
```bash
rm -rf ~/.cache/huggingface
pip install --upgrade transformers torch
```

### NewsAPI rate limit reached

The following measures are implemented:
- Fetch as much information as possible per request
- Use yfinance as fallback
- Demo data provided

### Docker container won't start
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
```bash
lsof -i :8000
lsof -i :3000
lsof -i :80
kill -9 <PID>
```

## 📄 License

MIT License

## 🤝 Contributing

Pull requests are welcome!

## 📧 Contact

If you have any issues or questions, please open an Issue.

## 🙏 Acknowledgements

- [FinBERT](https://huggingface.co/ProsusAI/finbert) - Sentiment analysis model
- [NewsAPI](https://newsapi.org/) - News data
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance data
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [React](https://reactjs.org/) - UI framework

---

**NewsSpY © 2026 | US Stock Sentiment Analysis Dashboard**

---

<a name="chinese"></a>
# 🇨🇳 中文

# NewsSpY - 美股情绪分析仪表盘

一款自动获取美股（相当于S&P 500）新闻，使用FinBERT AI模型进行情绪分析，并将评分可视化的Web应用程序。

## 🚀 功能特点

- **自动新闻采集**: 每日自动从NewsAPI和yfinance采集新闻
- **AI情绪分析**: 使用金融专用AI模型"FinBERT"进行情绪分析（正面/负面/中性）
- **情绪热力图**: 以瓦片形式可视化展示S&P 500各股票的情绪评分
- **股票详情**: 以折线图展示特定股票情绪评分的时间序列变化
- **搜索功能**: 从500家公司列表中搜索股票代码
- **实时更新**: 实时反映最新新闻和情绪评分

## 🛠 技术栈

### 后端
- **FastAPI**: 高性能Python Web框架
- **Python 3.10+**: 主要编程语言
- **FinBERT**: 金融专用AI情绪分析模型（Hugging Face Transformers）
- **SQLite**: 数据库（初始阶段）
- **NewsAPI**: 新闻数据来源
- **yfinance**: 从Yahoo Finance获取新闻

### 前端
- **React 18**: UI框架
- **Vite**: 快速构建工具
- **TypeScript**: 类型安全的JavaScript
- **Tailwind CSS**: 实用优先的CSS框架
- **Recharts**: 交互式数据可视化库
- **Axios**: HTTP客户端

### 基础设施
- **Docker**: 容器化
- **Docker Compose**: 多容器管理
- **Nginx**: 反向代理

## 📁 项目结构

```
newspy/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI应用入口
│   │   ├── config.py               # 配置文件
│   │   ├── database.py             # 数据库操作
│   │   ├── routes/
│   │   │   ├── auth.py            # 认证API
│   │   │   ├── sentiments.py      # 情绪评分API
│   │   │   ├── scores.py         # 评分API
│   │   │   └── articles.py       # 文章API
│   │   └── services/
│   │       ├── auth.py            # 认证服务
│   │       ├── sentiment_analyzer.py  # FinBERT情绪分析
│   │       └── score_calculator.py    # 评分计算
│   ├── batch/
│   │   ├── main.py                 # 批处理主程序
│   │   └── news_fetcher.py         # NewsAPI集成
│   ├── companies.json              # 企业主数据
│   ├── requirements.txt            # Python依赖
│   └── Dockerfile                # Docker镜像
├── frontend/
│   ├── src/
│   │   ├── main.tsx               # React入口
│   │   ├── App.tsx                # 主应用程序
│   │   ├── index.css              # 全局样式
│   │   ├── components/
│   │   │   ├── Heatmap.tsx        # 情绪热力图
│   │   │   ├── Search.tsx         # 搜索功能
│   │   │   └── StockDetail.tsx    # 股票详情
│   │   ├── services/
│   │   │   └── api.ts             # API客户端
│   │   └── types/
│   │       └── index.ts           # TypeScript类型定义
│   ├── package.json               # Node.js依赖
│   ├── vite.config.ts             # Vite配置
│   ├── tailwind.config.js         # Tailwind CSS配置
│   └── Dockerfile                 # Docker镜像
├── nginx/
│   └── nginx.conf                # Nginx反向代理配置
├── docker-compose.yml             # Docker Compose配置
├── .env.example                 # 环境变量模板
└── README.md                    # 项目文档
```

## 🚀 快速开始

### 前提条件

- Docker 20.10+（参见[安装指南](DOCKER_INSTALL.md)）
- Docker Compose 2.0+（或本地开发环境）
- Git

> **💡 如果未安装Docker**: 请参阅[Docker安装指南](DOCKER_INSTALL.md)。

### 安装

#### 方式1: 使用Shell脚本（最简单）

**⚡ 一键启动:**

```bash
./start_server.sh
```

该脚本自动执行以下操作：
- 停止并删除现有容器
- 清理未使用的Docker资源
- 使用Docker Compose启动服务器
- 健康检查并确认启动

**📱 访问应用程序:**
- 前端: http://localhost:3000
- 主页: http://localhost
- 后端API: http://localhost:8000/api/docs
- 健康检查: http://localhost:8000/api/health/

---

#### 方式2: 使用Docker Compose（推荐）

1. 克隆仓库
```bash
git clone <repository-url>
cd newspy
```

2. 设置环境变量
```bash
cp .env.example .env
# 编辑.env文件并设置NewsAPI密钥
```

3. 使用Docker Compose启动
```bash
docker-compose up -d
```

4. 访问应用程序
- 前端: http://localhost:3000
- 后端API: http://localhost:8000/api/docs
- 健康检查: http://localhost:8000/api/health/

#### 方式3: 本地开发（不使用Docker）

如果未安装Docker Compose，可以在本地运行。

##### 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from app.database import init_database; init_database()"

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

##### 启动前端（React + Vite）

```bash
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run dev
```

##### 访问应用程序
- 前端: http://localhost:3000
- 后端API: http://localhost:8000/api/docs
- 健康检查: http://localhost:8000/api/health/

#### 安装Docker Compose

**Linux:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

**Mac (使用Homebrew):**
```bash
brew install docker-compose
```

**Windows:**
安装Docker Desktop，其中包含Docker Compose。
https://www.docker.com/products/docker-desktop/

## 📊 API端点

### 认证API

#### 登录（获取Token）
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

#### 获取当前用户信息
```
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### 刷新Token
```
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

### 情绪评分API

#### 获取每日情绪评分（热力图用）
```
GET /api/sentiments/daily?target_date=YYYY-MM-DD
```

#### 按股票代码获取情绪历史（图表用）
```
GET /api/sentiments/{ticker}?days=30
```

#### 获取情绪摘要
```
GET /api/sentiments/summary
```

### 其他API

#### 健康检查
```
GET /api/health/
```

#### 模型状态
```
GET /api/model/status
```

完整API文档请访问 [http://localhost/api/docs](http://localhost/api/docs)。

## 🖥️ 服务器管理

### 启动服务器

**⚡ 使用Shell脚本（推荐）:**
```bash
./start_server.sh
```

**🔧 使用Docker Compose:**
```bash
docker-compose up -d
```

### 停止服务器
```bash
docker-compose down
```

### 重启服务器
```bash
docker-compose restart
```

### 检查服务器状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 所有日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### 重新构建容器
```bash
# 无缓存重新构建
docker-compose build --no-cache

# 重新构建特定服务
docker-compose build backend
docker-compose build frontend

# 重新构建并启动
docker-compose up -d --build
```

## 🔄 批处理

批处理按以下步骤执行：

1. **数据库初始化**: 创建表
2. **企业注册**: 从companies.json注册企业
3. **新闻获取**: 从NewsAPI获取过去24小时的新闻
4. **关键词过滤**: 按企业名称和关键词过滤新闻
5. **情绪分析**: 使用FinBERT执行情绪分析
6. **数据保存**: 将分析结果保存到数据库

### 手动执行

#### Docker环境
```bash
docker-compose exec backend python batch/main.py
```

#### 本地环境
```bash
cd backend
bash run_batch.sh

# 或直接执行
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python batch/main.py
```

### 定时执行（cron）
```bash
# 每天上午9点执行（Docker）
0 9 * * * cd /app && python batch/main.py

# 每天上午9点执行（本地）
0 9 * * * cd /path/to/backend && bash run_batch.sh
```

## 🎨 数据结构

### 企业主数据 (companies.json)

```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "keywords": ["Apple", "iPhone", "iPad", "Mac", "iOS", "Tim Cook"]
  }
]
```

### 数据库表

#### news_sentiments表

| 列名 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| ticker | TEXT | 股票代码（已索引） |
| published_at | TIMESTAMP | 新闻发布时间 |
| sentiment_score | REAL | FinBERT评分（-1.0 to 1.0） |
| label | TEXT | positive / negative / neutral |
| created_at | TIMESTAMP | 记录创建日期 |
| url_hash | TEXT | 新闻URL哈希值（唯一约束） |

## 🔧 配置

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| NEWSAPI_KEY | NewsAPI密钥 | demo |
| DATABASE_URL | 数据库路径 | newspy.db |
| JWT_SECRET_KEY | JWT Token签名密钥 | your-secret-key-change-this-in-production |
| ACCESS_TOKEN_EXPIRE_MINUTES | 访问Token有效期（分钟） | 60 |
| ALLOWED_ORIGINS | 允许的来源（逗号分隔） | http://localhost:3000 |

### 获取NewsAPI密钥

1. 在[NewsAPI](https://newsapi.org/)注册账号
2. 获取API密钥
3. 在`.env`文件中配置

## 📝 开发

### 快速开始（开发）
```bash
./start_server.sh

# 或手动启动
docker-compose up -d
```

### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 🐛 故障排除

### 服务器无法启动

**使用Shell脚本:**
```bash
./start_server.sh
```

**手动启动:**
```bash
docker-compose down
docker system prune -f
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

### FinBERT模型无法加载
```bash
rm -rf ~/.cache/huggingface
pip install --upgrade transformers torch
```

### 达到NewsAPI限制

已实施以下对策：
- 每次请求尽可能获取更多信息
- 使用yfinance作为备用
- 提供演示数据

### Docker容器无法启动
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
docker-compose build --no-cache
docker-compose up -d
```

### 端口已被占用
```bash
lsof -i :8000
lsof -i :3000
lsof -i :80
kill -9 <PID>
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Pull Request！

## 📧 联系方式

如有问题或疑问，请开启Issue。

## 🙏 致谢

- [FinBERT](https://huggingface.co/ProsusAI/finbert) - 情绪分析模型
- [NewsAPI](https://newsapi.org/) - 新闻数据
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance数据
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [React](https://reactjs.org/) - UI框架

---

**NewsSpY © 2026 | US Stock Sentiment Analysis Dashboard**
