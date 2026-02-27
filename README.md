# LLM Consensus Engine

A production-ready application designed to robustly evaluate generated code by acting as a "judge" using multiple large language models. The engine queries APIs from OpenAI, Anthropic, and Gemini simultaneously, structures their outputs natively via Pydantic matching schemas, aggregates the results, checks for model disagreements, calculates a finalized risk severity score, and stores the analytics in a persistent database. Let AI review AI.

## Project Architecture

Designed with a clean, extensible structure separating concerns:
- **`core/`**: Configuration, logging, database connections (SQLAlchemy engine/session).
- **`models/`**: SQLAlchemy domain models representing relational database records.
- **`schemas/`**: Pydantic schemas standardizing inputs and outputs strictly.
- **`engine/`**: The consensus brain modules:
  - `reviewers.py`: LiteLLM implementation wrapping multi-LLM API calls.
  - `diff_analyzer.py`: Utilizes python's `difflib` for AST/line-based comparison.
  - `aggregator.py`: Detects consensus deviations among reviews and assigns unified severity.
  - `reporter.py`: Consumes consensus analytics to output structured markdown.
  - `dispatcher.py`: Asynchronous event orchestrator binding the engine pipeline.
- **`api/`**: FastAPI endpoints that trigger the pipeline asynchronously from a REST interface.
- **`dashboard/`**: Streamlit visualization frontend connecting back into the SQLite DB to track analytical metrics visually.

## Quick Start (Docker)

1. **Configure Environment**
Create an `.env` file at the root folder with your API Keys (those supported by `litellm`):

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
```

*(You can also override model constants by setting `PRIMARY_MODEL`, `SECONDARY_MODEL`, and `TERTIARY_MODEL`)*

2. **Deploy Platform**
Simply deploy using `docker-compose`:

```bash
docker-compose up --build -d
```

3. **Interact**
- Streamlit UI Dashboard: [http://localhost:8501](http://localhost:8501)
- FastAPI Documentation / Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

Run a test code submisison in the Dashboard to stream it through the models to review!

## Local Development (Without Docker)

Creating your python virtual environment correctly:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run FastAPI backend locally automatically instancing the `.db` layer:
```bash
uvicorn main:app --reload
```

Run Streamlit frontend matching the same local URL config:
```bash
streamlit run dashboard/app.py
```
