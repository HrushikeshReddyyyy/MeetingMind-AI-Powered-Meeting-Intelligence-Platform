# MeetingMind: AI-Powered Meeting Intelligence Platform

MeetingMind automates meeting documentation through AI-powered transcription, smart summaries, and action item tracking. Built with no-code integration tools (Otter.ai + Notion + Zapier), it transforms unproductive meetings into actionable insights, automatically distributing summaries and tracking follow-ups to boost team accountability and productivity.

## Features

- **AI-Powered Summaries** - Automatically generate concise meeting summaries from transcripts
- **Action Item Extraction** - AI identifies action items, assignees, priorities, and deadlines
- **Key Decision Tracking** - Captures and highlights important decisions made during meetings
- **Meeting Analytics** - Sentiment analysis, engagement scoring, topic tagging, and trends
- **Otter.ai Integration** - Fetch transcriptions directly from Otter.ai meetings
- **Notion Sync** - Automatically create Notion pages with meeting summaries and action items
- **Zapier Automation** - Trigger workflows for summary distribution, action item assignments, and follow-up reminders
- **Dashboard** - Real-time overview of meetings, action items, and platform impact

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Python, FastAPI, SQLAlchemy |
| Frontend | React, Vite, React Router |
| AI Engine | OpenAI GPT (with fallback processing) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Transcription | Otter.ai |
| Documentation | Notion API |
| Automation | Zapier Webhooks |
| Containerization | Docker, Docker Compose |

## Project Structure

```
MeetingMind/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup & session management
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── meetings.py      # Meeting CRUD & processing endpoints
│   │   │   ├── action_items.py  # Action item management endpoints
│   │   │   ├── analytics.py     # Dashboard & analytics endpoints
│   │   │   └── integrations.py  # Integration config endpoints
│   │   └── services/
│   │       ├── ai_engine.py     # OpenAI-powered AI processing
│   │       ├── meeting_processor.py  # Processing pipeline orchestrator
│   │       ├── otter_service.py # Otter.ai integration
│   │       ├── notion_service.py # Notion integration
│   │       └── zapier_service.py # Zapier webhook integration
│   ├── tests/                   # Backend test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # App layout with routing
│   │   ├── api.js               # API client
│   │   ├── index.css            # Global styles
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # Overview dashboard
│   │   │   ├── Meetings.jsx     # Meeting list & creation
│   │   │   ├── MeetingDetail.jsx # Meeting detail with tabs
│   │   │   ├── ActionItems.jsx  # Action item management
│   │   │   ├── Analytics.jsx    # Analytics & insights
│   │   │   └── Settings.jsx     # Integration configuration
│   │   └── test/                # Frontend test suite
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Docker & Docker Compose

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend will be available at `http://localhost:5173` and the API at `http://localhost:8000`.

### Docker Setup

```bash
# Copy and configure environment
cp backend/.env.example backend/.env

# Build and start all services
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

### Meetings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meetings` | List all meetings |
| POST | `/api/meetings` | Create a new meeting |
| GET | `/api/meetings/{id}` | Get meeting details |
| PUT | `/api/meetings/{id}` | Update a meeting |
| DELETE | `/api/meetings/{id}` | Delete a meeting |
| POST | `/api/meetings/{id}/transcript` | Upload transcript & process |
| POST | `/api/meetings/{id}/process` | Reprocess a meeting |

### Action Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/action-items` | List action items |
| POST | `/api/action-items` | Create action item |
| PUT | `/api/action-items/{id}` | Update action item |
| DELETE | `/api/action-items/{id}` | Delete action item |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Dashboard statistics |
| GET | `/api/analytics/meetings-over-time` | Meeting trends |
| GET | `/api/analytics/action-item-summary` | Action item breakdown |

### Integrations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/integrations` | List all integrations |
| PUT | `/api/integrations/{service}` | Update integration config |
| POST | `/api/integrations/{service}/test` | Test connection |

## Running Tests

### Backend Tests
```bash
cd backend
pytest -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Configuration

All configuration is managed through environment variables in the `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI processing | For AI features |
| `OTTER_EMAIL` | Otter.ai account email | For transcription |
| `OTTER_PASSWORD` | Otter.ai account password | For transcription |
| `NOTION_API_KEY` | Notion integration API key | For Notion sync |
| `NOTION_DATABASE_ID` | Notion database ID | For Notion sync |
| `ZAPIER_WEBHOOK_SUMMARY` | Zapier webhook for summaries | For automation |
| `ZAPIER_WEBHOOK_ACTION_ITEMS` | Zapier webhook for action items | For automation |
| `ZAPIER_WEBHOOK_FOLLOWUP` | Zapier webhook for follow-ups | For automation |

## Milestones

1. **Platform Setup & Integration** (Weeks 1-2): Configure Otter.ai transcription, build Notion database templates, and connect Zapier workflows for automated distribution
2. **AI Training & Testing** (Week 3): Train AI to identify action items and key decisions, test with 10 internal meetings, and refine summary formats
3. **Company Rollout** (Week 4): Deploy across all departments, train 50+ users, implement feedback system, activate analytics tracking

## Cost

- Setup: $400 (one-time configuration)
- Monthly: $85 (Otter.ai Business $20, Notion Team $15, Zapier $20, AI API $30)
- Break-even: Month 2

## Impact

- Save 5 hours/week per team on meeting notes and follow-ups
- Cost Savings: $45,000/year (IT staff time recovered)
- 100% meeting documentation vs. the current 30%
- Instant searchable archive of all company decisions
- 3x faster action item completion with automated tracking
