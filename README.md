<div align="center">

# NewsSpY

### 🤖 AI-Powered Financial News Sentiment Analysis Platform

**Transform raw financial news into actionable market insights** using FinBERT — the state-of-the-art NLP model for financial sentiment analysis.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

[Features](#-key-features) • [Quick Start](#-quick-start) • [API](#-api-endpoints) • [Architecture](#-architecture)

</div>

---

## 🎯 Why This Project Exists

Financial markets move on information — but the volume of daily news is overwhelming. Traders and analysts spend hours manually sifting through headlines to gauge market sentiment.

**NewsSpY automates this process** by:
- **Aggregating** financial news for 44 major US companies in real-time
- **Analyzing** sentiment using FinBERT (ProsusAI's financial NLP model)
- **Visualizing** trends through an interactive dashboard

Whether you're a quantitative trader, financial analyst, or developer exploring NLP applications, NewsSpY provides a complete, production-ready reference architecture for AI-powered financial analysis.

---

## 📸 Demo

### Dashboard Preview

![Dashboard Demo](./docs/demo.gif)

*Neon-themed Investment Dashboard · Sentiment Heatmap · Time-series Charts*

### Sentiment Heatmap

| Ticker | Company | Sentiment Score | Articles Analyzed |
|--------|---------|-----------------|-------------------|
| NVDA | NVIDIA Corp | +0.89 | 142 |
| AAPL | Apple Inc. | +0.76 | 98 |
| TSLA | Tesla Inc. | -0.34 | 87 |

---

## ✨ Key Features

- **🧠 AI-Powered Analysis** — FinBERT sentiment analysis optimized for financial text
- **📊 Real-Time Dashboard** — Interactive charts and heatmaps built with React & Recharts
- **🔔 Smart Filtering** — Pre-market focused news (JST 06:00–22:00) for actionable insights
- **🔄 Automated Processing** — Daily batch processing with configurable schedules
- **🐳 Production-Ready** — Fully containerized with Docker & Docker Compose
- **⚡ Fast API** — RESTful endpoints powered by FastAPI
- **📈 44 Companies Tracked** — Comprehensive coverage of US large-cap stocks

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Sources                              │
│  ┌──────────────┐            ┌──────────────┐                   │
│  │   GNews API  │            │  yfinance    │                   │
│  └──────┬───────┘            └──────┬───────┘                   │
└─────────┼──────────────────────────┼────────────────────────────┘
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Sentiment Analysis Engine                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   FinBERT NLP Model                      │    │
│  │           (ProsusAI/finbert on HuggingFace)             │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    JSON Files                            │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Server                        │    │
│  │              (Port 8000 behind Nginx)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Frontend Dashboard                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │      React 18 + TypeScript + TailwindCSS + Recharts     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | FastAPI, Python 3.10+ | High-performance API framework |
| **AI/NLP** | FinBERT | Financial sentiment analysis model |
| **Data Sources** | GNews API, yfinance | News aggregation & market data |
| **Frontend** | React 18, TypeScript, Vite | Modern reactive UI |
| **Styling** | TailwindCSS | Utility-first CSS framework |
| **Charts** | Recharts | Declarative data visualization |
| **Infrastructure** | Docker, Docker Compose, Nginx | Containerization & reverse proxy |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- GNews API key ([get one here](https://gnews.io/))

### Installation

```bash
# Clone the repository
git clone https://github.com/yuina368/NewsSpY.git
cd NewsSpY

# Configure your API key
echo "GNEWS_API_KEY=your_api_key_here" > .env

# Launch the full stack
docker-compose up -d

# Fetch news and run sentiment analysis
docker exec newspy-backend python -m batch.main

# Access the dashboard
open http://localhost
```

| URL | Description |
|:----|:------------|
| http://localhost | 📊 Dashboard |
| http://localhost/api/docs | 📖 Swagger API Docs |

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/companies/` | GET | List all tracked companies |
| `/api/scores/ranking/{date}` | GET | Sentiment ranking by date |
| `/api/scores/{ticker}` | GET | Historical sentiment scores |
| `/api/articles/?ticker={ticker}` | GET | News articles by ticker |
| `/api/sentiments/{ticker}` | GET | Raw sentiment data |

---

## 💡 Use Cases

- **Quantitative Trading** — Generate signals from news sentiment trends
- **Financial Analysis** — Quick overview of market perception
- **NLP Research** — Reference implementation for financial text analysis
- **Portfolio Monitoring** — Track sentiment across holdings
- **Educational** — Learn production ML/AI system architecture

---

## 🗺️ Roadmap

- [ ] Additional sentiment models (VADER, BERT variants)
- [ ] Multi-language news support
- [ ] Real-time WebSocket updates
- [ ] Custom time range filtering
- [ ] Export to CSV/Excel
- [ ] Alert system for sentiment spikes
- [ ] Backtesting framework for sentiment-based strategies

---

## 📁 Project Structure

```
NewsSpY/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration settings
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routes/              # API route handlers
│   │   │   ├── articles.py      # Article endpoints
│   │   │   ├── scores.py        # Score endpoints
│   │   │   ├── sentiments.py    # Sentiment endpoints
│   │   │   ├── batch.py         # Batch processing endpoints
│   │   │   └── auth.py          # Authentication endpoints
│   │   └── services/            # Business logic
│   │       ├── json_storage.py         # JSON file storage
│   │       ├── sentiment_analyzer.py  # FinBERT integration
│   │       └── score_calculator.py   # Score calculation
│   ├── batch/                   # Batch processing scripts
│   │   ├── main.py              # Main batch processor
│   │   └── news_fetcher.py      # News fetching logic
│   ├── companies.json           # Company data
│   ├── Dockerfile               # Backend Docker config
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main application component
│   │   ├── main.tsx             # Entry point
│   │   ├── components/          # React components
│   │   │   ├── Heatmap.tsx      # Sentiment heatmap
│   │   │   ├── StockDetail.tsx  # Stock detail modal
│   │   │   └── Search.tsx       # Company search
│   │   ├── services/
│   │   │   └── api.ts           # API client
│   │   └── types/
│   │       └── index.ts         # TypeScript types
│   ├── Dockerfile               # Frontend Docker config
│   ├── package.json             # Node dependencies
│   └── vite.config.ts           # Vite configuration
├── nginx/
│   └── nginx.conf               # Nginx reverse proxy config
├── docker-compose.yml           # Docker Compose orchestration
└── README.md                    # This file
```

---

## 📊 Tracked Companies (44)

<details>
<summary><b>View all tickers by sector</b></summary>
<br/>

| Sector | Tickers |
|:-------|:--------|
| 💻 Technology | `AAPL` `MSFT` `GOOGL` `AMZN` `TSLA` `META` `NVDA` `NFLX` `CRM` `ADBE` |
| 🏦 Financials | `JPM` `BAC` `WFC` `GS` `MS` `BLK` `ICE` `CME` `V` `MA` `AXP` |
| 🏥 Healthcare | `JNJ` `UNH` `PFE` `ABBV` `MRK` `TMO` `LLY` |
| 🛒 Consumer | `WMT` `KO` `PEP` `COST` `MCD` `NKE` `LOW` |
| ⚡ Energy / Industrial | `XOM` `CVX` `BA` `HON` `GE` |
| 📡 Telecom / Media | `VZ` `T` `CMCSA` `DIS` |

</details>

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**[⬆ Back to Top](#newspy)**

Made with ❤️ by [yuina368](https://github.com/yuina368)

**[FinBERT](https://huggingface.co/ProsusAI/finbert)** · **[GNews API](https://gnews.io/)** · **[yfinance](https://pypi.org/project/yfinance/)**

</div>
