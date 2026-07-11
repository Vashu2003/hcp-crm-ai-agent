# HCP CRM — AI Agent for Pharma Field Sales

An **AI-first CRM module** that lets pharmaceutical field-sales reps log their interactions
with **HCPs (Healthcare Professionals / doctors)** through **two input modes that share one
AI agent**:

1. **Structured form** — fill in the fields, the agent summarizes & extracts entities.
2. **Conversational chat** — type naturally ("Met Dr. Sharma today, discussed Xarelto…") and
   the agent routes your message to the right tool.

Both modes are powered by the **same LangGraph agent** with **5 tools**, so natural language
and structured input run through identical AI logic.

> Built as a full-stack demonstration of agentic LLM application design: LangGraph tool-calling,
> a Groq-hosted LLM, FastAPI, PostgreSQL, and a React + Redux Toolkit frontend.

---

## ✨ Features

- **Log Interaction** with automatic LLM **summarization + entity extraction** (HCP name,
  specialty, products, sentiment, key topics, follow-up date, samples given).
- **Edit** any past interaction — the AI summary recomputes on note changes.
- **Search / List** interactions by HCP, product, sentiment, or date range.
- **Schedule Follow-up** with an AI **next-best-action** suggestion.
- **Generate Summary Report** — an LLM narrative across many interactions
  ("summarize my last month with Dr. Sharma").
- One agent, two front doors: **Form** and **Chat** both call the same tools.

**Beyond the brief (extra features):**
- **Analytics stats row** — live counts of interactions, HCPs engaged, sentiment split, follow-ups due.
- **Follow-ups panel** — AI-created follow-ups with overdue badges and one-click **mark-done**.
- **Markdown chat** — agent replies render tables / lists / bold for a clean, readable conversation.

---

## 🏗️ Architecture

```
                 ┌──────────────────────────────────────────────┐
   Form mode ───▶│  FastAPI  /interactions  (deterministic)      │
                 │        │                                      │
                 │        ▼   shared service layer               │
   Chat mode ───▶│  FastAPI  /chat  ─▶  LangGraph agent          │
                 │                        │  ChatGroq + 5 tools  │
                 │                        ▼                       │
                 │                   summarize_and_extract (LLM)  │
                 │                        │                       │
                 │                        ▼                       │
                 │                   PostgreSQL (SQLAlchemy)      │
                 └──────────────────────────────────────────────┘
```

- **LangGraph** `StateGraph(MessagesState)`: `llm` node (ChatGroq bound to 5 tools) →
  conditional edge → `ToolNode` → loops back until the model returns a final answer.
- The **Form flow** calls the **same service layer** the `log_interaction` tool uses, so both
  input modes share summarization/extraction and persistence.

### Tech stack

| Layer | Tech |
|---|---|
| Frontend | React + TypeScript, Redux Toolkit, Vite, Inter font |
| Backend | Python, FastAPI |
| AI agent | LangGraph (tool-calling StateGraph) |
| LLM | Groq — `openai/gpt-oss-20b` (default) / `llama-3.3-70b-versatile` |
| Database | PostgreSQL (SQLAlchemy ORM) |

> **Note on the model:** the assignment specified `gemma2-9b-it`, which Groq has since
> **decommissioned**. The model is fully configurable via `GROQ_MODEL`; the app defaults
> to `openai/gpt-oss-20b` (reliable tool-calling, comfortable free-tier budget), and the
> assignment's listed alternative `llama-3.3-70b-versatile` works by setting one env var.

---

## 🔧 The 5 Agent Tools

| # | Tool | What it does |
|---|---|---|
| 1 | `log_interaction` | Create an interaction; LLM summary + entity extraction; auto-creates a follow-up if one is implied. |
| 2 | `edit_interaction` | Update an interaction by id; recomputes AI summary if notes change. |
| 3 | `search_interactions` | Query by HCP, product, sentiment, date range. |
| 4 | `schedule_followup` | Set a follow-up; if no action given, LLM suggests the next-best-action. |
| 5 | `generate_summary_report` | LLM narrative report across filtered interactions. |

---

## 🗄️ Data model

- **HCP** — `id, name, specialty, organization, notes, created_at`
- **Interaction** — `id, hcp_id, rep_name, date, channel, product_discussed, raw_notes,
  llm_summary, extracted_entities (JSON), sentiment, created_at, updated_at`
- **FollowUp** — `id, interaction_id, hcp_id, due_date, action, status, created_at`

---

## 🚀 Setup & run

### Prerequisites
- Python 3.11+, Node 18+, PostgreSQL 14+
- A free **Groq API key** — https://console.groq.com

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit .env
#   GROQ_API_KEY=gsk_...
#   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/aivoa_crm

python -m app.seed        # create tables + seed sample HCPs/interactions
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### Environment variables

| Var | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key (required). |
| `GROQ_MODEL` | `openai/gpt-oss-20b` (default) or `llama-3.3-70b-versatile`. |
| `DATABASE_URL` | SQLAlchemy Postgres URL. |
| `FRONTEND_ORIGIN` | CORS origin for the Vite dev server. |

---

## 📸 Screenshots

**Dashboard** — stats row, Log Interaction (Form/Chat), live interaction list, and follow-ups:

![Dashboard](docs/screenshots/dashboard.png)

**Form mode** — structured logging with live AI summary & entity extraction:

![Form mode](docs/screenshots/form-mode.png)

**Chat mode** — natural language routed to the right tool by the LangGraph agent
(note the `🛠 search_interactions` tool chip for transparency):

![Chat mode](docs/screenshots/chat-mode.png)

---

## 📄 License

MIT © 2026 Vashu Singh
