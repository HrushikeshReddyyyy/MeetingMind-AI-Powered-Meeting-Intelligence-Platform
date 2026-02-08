<div align="center">

# MeetingMind

### AI-Powered Meeting Intelligence Platform

**Stop losing decisions in meeting chaos. Start turning every conversation into action.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-38%20Passing-brightgreen?style=for-the-badge)](.)

</div>

---

## The Problem

Teams spend **5+ hours per week** writing meeting notes, chasing action items, and wondering _"Wait, what did we decide?"_ Only **30%** of meetings get properly documented. Critical decisions vanish. Action items slip through the cracks.

## The Solution

MeetingMind is a full-stack platform that **automates your entire meeting workflow**:

```
Meeting Recording  -->  AI Transcription  -->  Smart Summary
                                                    |
                                           +--------+--------+
                                           |        |        |
                                       Decisions  Action   Analytics
                                                  Items
                                           |        |        |
                                           v        v        v
                                        Notion   Zapier   Dashboard
                                        (docs)  (assign)  (insights)
```

Paste a transcript (or connect Otter.ai), and MeetingMind instantly generates a summary, pulls out every action item with owners and deadlines, logs key decisions, and pushes everything to Notion and Zapier -- all in seconds.

---

## What It Does

| Capability | How It Works |
|---|---|
| **Smart Summaries** | AI reads the full transcript and produces a concise, professional summary highlighting what matters |
| **Action Item Extraction** | Automatically identifies tasks, assigns owners, sets priorities (high/medium/low), and parses deadline hints like _"by next Friday"_ |
| **Decision Capture** | Finds and lists every decision made -- no more digging through notes to recall what was agreed |
| **Meeting Analytics** | Scores engagement (1-100), detects sentiment (positive/neutral/negative), counts speakers, and tags topics |
| **Notion Sync** | Creates a structured Notion page per meeting with summary, decisions as bullet points, and action items as to-do checkboxes |
| **Zapier Automation** | Fires webhooks to distribute summaries via email/Slack, assign action items in project tools, and send follow-up reminders for overdue tasks |
| **Otter.ai Integration** | Pulls transcripts directly from Otter.ai -- connect once and it works automatically |

---

## Tech Stack

```
Frontend                    Backend                     Integrations
---------------------       ----------------------      ---------------------
React 18 + Vite             Python 3.11 + FastAPI       Otter.ai (transcribe)
React Router v6             SQLAlchemy (async ORM)      Notion API (document)
Pure CSS (no framework)     Pydantic v2 (validation)    Zapier Webhooks (automate)
                            SQLite / PostgreSQL          OpenAI GPT (AI engine)
                            Docker + Compose
```

---

## Project Structure

```
MeetingMind/
|
+-- backend/
|   +-- app/
|   |   +-- main.py                  # FastAPI app with CORS, lifespan, routing
|   |   +-- config.py                # Pydantic settings from .env
|   |   +-- database.py              # Async SQLAlchemy engine + session factory
|   |   +-- models.py                # Meeting, ActionItem, Analytics, IntegrationConfig
|   |   +-- schemas.py               # Request/response validation schemas
|   |   +-- routers/
|   |   |   +-- meetings.py          # CRUD + transcript upload + processing trigger
|   |   |   +-- action_items.py      # Action item management with filters
|   |   |   +-- analytics.py         # Dashboard stats + trend data
|   |   |   +-- integrations.py      # Integration config + connection testing
|   |   +-- services/
|   |       +-- ai_engine.py         # OpenAI calls + fallback NLP processing
|   |       +-- meeting_processor.py  # Pipeline: AI -> Notion -> Zapier
|   |       +-- otter_service.py     # Otter.ai auth + transcript fetch
|   |       +-- notion_service.py    # Notion page creation + updates
|   |       +-- zapier_service.py    # Webhook triggers for 3 event types
|   +-- tests/                       # 31 async API + unit tests
|   +-- requirements.txt
|   +-- Dockerfile
|
+-- frontend/
|   +-- src/
|   |   +-- App.jsx                  # Layout with sidebar navigation
|   |   +-- api.js                   # Fetch-based API client (15 endpoints)
|   |   +-- index.css                # Complete design system (CSS variables)
|   |   +-- pages/
|   |       +-- Dashboard.jsx        # Stats grid + recent meetings + pending items
|   |       +-- Meetings.jsx         # List with search/filter + create modal
|   |       +-- MeetingDetail.jsx    # Tabbed view: Summary | Actions | Transcript | Analytics
|   |       +-- ActionItems.jsx      # Filterable table with inline status updates
|   |       +-- Analytics.jsx        # Bar charts + breakdowns + impact metrics
|   |       +-- Settings.jsx         # Integration cards with toggle + test buttons
|   +-- test/                        # 7 component + API client tests
|   +-- package.json
|   +-- Dockerfile
|
+-- docker-compose.yml               # Backend + Nginx-fronted frontend
+-- README.md
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/HrushikeshReddyyyy/MeetingMind-AI-Powered-Meeting-Intelligence-Platform.git
cd MeetingMind-AI-Powered-Meeting-Intelligence-Platform

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys (see Configuration section below)

# Launch everything
docker-compose up --build
```

Open http://localhost:3000 (frontend) or http://localhost:8000/docs (API docs).

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # Then edit .env with your keys
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (frontend proxies API calls to :8000 automatically).

---

## How to Use It

### 1. Create a meeting
Go to **Meetings** > **New Meeting**. Give it a title, date, and list of participants.

### 2. Add a transcript
Open the meeting and paste a transcript into the text area. Transcripts work best in this format:
```
Alice: Let's discuss the Q4 roadmap and budget allocation.
Bob: I propose we allocate 60% to mobile development.
Alice: Agreed. Bob, can you prepare a detailed breakdown by next Friday?
Charlie: I'll handle the vendor evaluation. We decided to go with AWS over GCP.
```

### 3. Hit "Upload & Process"
MeetingMind runs the full pipeline in the background:
- Generates a multi-paragraph summary
- Extracts action items: _"Prepare detailed breakdown"_ (Bob, High, due Friday)
- Captures decisions: _"Allocate 60% to mobile"_, _"Go with AWS over GCP"_
- Computes analytics: word count, speaker count, sentiment, engagement score
- Syncs to Notion (if configured)
- Fires Zapier webhooks (if configured)

### 4. Track everything
Use the **Action Items** page to filter by status/priority, check off completed items, and catch overdue tasks. The **Analytics** page shows trends over time and your team's completion rate.

---

## API Reference

### Meetings
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/meetings` | List meetings (filter by `?status=` or `?search=`) |
| `POST` | `/api/meetings` | Create a meeting |
| `GET` | `/api/meetings/{id}` | Full meeting detail with action items + analytics |
| `PUT` | `/api/meetings/{id}` | Update meeting fields |
| `DELETE` | `/api/meetings/{id}` | Delete meeting and all associated data |
| `POST` | `/api/meetings/{id}/transcript` | Upload transcript and trigger AI processing |
| `POST` | `/api/meetings/{id}/process` | Re-run AI processing on existing transcript |

### Action Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/action-items` | List items (filter by `?status=`, `?priority=`, `?assignee=`) |
| `POST` | `/api/action-items?meeting_id=` | Create an action item |
| `PUT` | `/api/action-items/{id}` | Update status, priority, assignee, etc. |
| `DELETE` | `/api/action-items/{id}` | Delete an action item |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/dashboard` | Aggregated stats (totals, rates, averages) |
| `GET` | `/api/analytics/meetings-over-time?days=30` | Daily meeting counts |
| `GET` | `/api/analytics/action-item-summary` | Breakdown by status and priority |

### Integrations
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/integrations` | List all 4 integrations with status |
| `PUT` | `/api/integrations/{service}` | Enable/disable a service |
| `POST` | `/api/integrations/{service}/test` | Test connection to a service |

Full interactive docs available at **http://localhost:8000/docs** when the server is running.

---

## Configuration

Copy `backend/.env.example` to `backend/.env` and fill in the values you need:

```bash
# Required for AI-powered features (summaries, action items, analytics)
OPENAI_API_KEY=sk-...

# Optional: Otter.ai auto-transcription
OTTER_EMAIL=you@company.com
OTTER_PASSWORD=your-password

# Optional: Auto-sync meeting docs to Notion
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=abc123...

# Optional: Zapier workflow automation
ZAPIER_WEBHOOK_SUMMARY=https://hooks.zapier.com/hooks/catch/...
ZAPIER_WEBHOOK_ACTION_ITEMS=https://hooks.zapier.com/hooks/catch/...
ZAPIER_WEBHOOK_FOLLOWUP=https://hooks.zapier.com/hooks/catch/...
```

> **Note:** MeetingMind works without any API keys -- the AI engine has built-in fallback processing that uses keyword extraction and NLP heuristics. API keys unlock the full GPT-powered experience.

---

## Running Tests

```bash
# Backend (31 tests)
cd backend && pytest -v

# Frontend (7 tests)
cd frontend && npm test
```

All **38 tests** cover:
- Meeting CRUD operations and transcript processing
- Action item lifecycle (create, filter, update status, delete)
- Dashboard statistics and analytics aggregation
- Integration configuration and connection testing
- AI engine fallback processing (summaries, action items, decisions, analytics)
- React component rendering and API client behavior

---

## Roadmap

- [x] Core meeting CRUD with transcript upload
- [x] AI-powered summary generation and action item extraction
- [x] Otter.ai, Notion, and Zapier integrations
- [x] Analytics dashboard with engagement scoring
- [x] Docker containerization
- [ ] Real-time collaborative meeting notes (WebSocket)
- [ ] Calendar sync (Google Calendar / Outlook)
- [ ] Slack & Microsoft Teams bot for instant summaries
- [ ] Multi-language transcript support
- [ ] Custom AI prompt templates per team
- [ ] Role-based access control and team workspaces
- [ ] PostgreSQL migration for production deployments
- [ ] Export meetings to PDF / Markdown

---

## Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Make** your changes and add tests
4. **Run** tests to make sure everything passes:
   ```bash
   cd backend && pytest -v
   cd frontend && npm test
   ```
5. **Commit** with a clear message: `git commit -m "Add your feature"`
6. **Push** to your fork: `git push origin feature/your-feature`
7. **Open** a Pull Request

### Guidelines
- Follow existing code style and project structure
- Add tests for new API endpoints or services
- Update the README if you add new features or change configuration
- Keep PRs focused -- one feature or fix per PR

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built by [Hrushikesh Reddy](https://github.com/HrushikeshReddyyyy)**

_Turn meetings into momentum._

</div>
