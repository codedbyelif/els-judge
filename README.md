# LLM Consensus Engine

A production-ready application that evaluates generated code using multiple large language models as judges. The engine queries OpenAI, Anthropic, and Gemini simultaneously, structures their outputs via Pydantic schemas, aggregates results, detects disagreements, calculates a finalized risk score, and stores analytics in a database.

Built by [codedbyelif](https://github.com/codedbyelif)

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/codedbyelif/ai-code-judge.git
cd ai-code-judge
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root and add your API keys:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
```

You can also optionally override the default models:

```env
PRIMARY_MODEL=gpt-4o
SECONDARY_MODEL=claude-3-5-sonnet-20240620
TERTIARY_MODEL=gemini/gemini-1.5-pro
```

### 5. Run the project

**Option A — Run everything with one command:**

```bash
bash start.sh
```

This starts both the FastAPI backend (port 8000) and the Streamlit dashboard (port 8501).

**Option B — Run services separately:**

Terminal 1 — Backend:
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Terminal 2 — Dashboard:
```bash
source venv/bin/activate
streamlit run dashboard/app.py --server.port=8501
```

### 6. Open in browser

- **Dashboard:** [http://localhost:8501](http://localhost:8501)
- **API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## How to Use

1. Open the dashboard at `http://localhost:8501`
2. Paste your **Original Code** in the first text area
3. Paste the **Suggested Code** in the second text area
4. Click **"Run Consensus Pipeline"**
5. Wait for GPT-4o, Claude, and Gemini to analyze the code
6. View the risk score, severity level, and detailed report

---

## Project Architecture

```
ai-code-judge/
├── main.py              # FastAPI app entry point
├── start.sh             # One-command launcher for both services
├── requirements.txt     # Python dependencies
├── .env                 # API keys (create this yourself)
├── core/
│   ├── config.py        # Settings & environment variables
│   └── database.py      # SQLAlchemy engine & session
├── models/
│   └── domain.py        # Database models (Submission, FinalVerdict)
├── schemas/
│   └── api.py           # Pydantic request/response schemas
├── engine/
│   ├── reviewers.py     # LiteLLM multi-model API calls
│   ├── diff_analyzer.py # Code diff comparison
│   ├── aggregator.py    # Consensus detection & scoring
│   ├── reporter.py      # Markdown report generation
│   └── dispatcher.py    # Pipeline orchestrator
├── api/
│   └── routes.py        # FastAPI REST endpoints
└── dashboard/
    ├── app.py           # Streamlit UI
    └── translations.py  # EN/TR language support
```

---

## Docker (Alternative)

```bash
docker-compose up --build -d
```

- Dashboard: [http://localhost:8501](http://localhost:8501)
- API: [http://localhost:8000/docs](http://localhost:8000/docs)
