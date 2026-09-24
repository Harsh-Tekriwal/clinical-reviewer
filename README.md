# AI Clinical Document Reviewer

An end-to-end web application that takes clinical documentation — typed
text, an image, or a PDF, including scanned or handwritten pages — and
returns a structured clinical review: a short **Report Summary** plus a
**detailed structured breakdown** (symptoms, diagnoses, medications, vitals,
allergies, concerns, missing information, inconsistencies, and items that
need human review).

> ⚠️ All clinical data used in this project is **synthetic**. This is a
> student assignment, not a medical device, and is not intended for real
> clinical use or advice.

## Features

- Submit clinical notes as plain text, or upload an image / PDF
- Handles typed, scanned, and handwritten documents in one pipeline
- Clear loading and error states
- Structured report: a short summary plus detailed sections
- History of previously processed reports, with status and timestamps
- Frontend and backend fully separated, communicating over a REST API

## Tech stack

| Layer | Choice | Why (short version — full reasoning in `docs/TECHNICAL_DECISIONS.md`) |
|---|---|---|
| Frontend | React + Vite | minimal config, deploys free on Vercel |
| Backend | FastAPI (Python) | async, auto API docs, natural fit for the AI/ML ecosystem |
| AI/ML | Google Gemini API | native multimodal reading of text/image/PDF + schema-enforced JSON output, in one call |
| Database | PostgreSQL (prod) / SQLite (local) | same SQLAlchemy code works against both |
| Deployment | Render (backend + DB) + Vercel (frontend) | both have real free tiers |

## Repository structure

```
.
├── backend/
│   ├── main.py               # FastAPI app + routes
│   ├── database.py           # DB engine/session setup
│   ├── models.py              # SQLAlchemy ORM model
│   ├── schemas.py             # Pydantic schemas (API + AI output schema)
│   ├── ai_service.py          # Gemini integration ("AI/ML layer")
│   ├── document_service.py    # File validation ("document processing" layer)
│   ├── tests/test_basic.py    # Basic validation tests (no live API calls)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/        # SubmitForm, ReportView, ReportsList
│   ├── package.json
│   └── .env.example
└── docs/
    ├── ARCHITECTURE.md         # diagram + component/request-flow explanation
    ├── AI_ML_DESIGN.md         # required AI/ML design documentation
    └── TECHNICAL_DECISIONS.md  # required technical-decisions documentation
```

## Architecture

Full diagram and explanation in `docs/ARCHITECTURE.md`. In short:

```
Browser (React) → FastAPI backend → document_service (validation)
                                   → ai_service (Gemini, structured output)
                                   → PostgreSQL (persistence)
```

## Setup — Backend

1. `cd backend`
2. `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. `cp .env.example .env` and fill in `GEMINI_API_KEY` (free key from
   https://aistudio.google.com/apikey — no credit card needed). Leave
   `DATABASE_URL` as the default SQLite URL for local dev.
5. `uvicorn main:app --reload`
6. API is live at `http://localhost:8000` — interactive docs at
   `http://localhost:8000/docs`

Run the tests with `pytest` from inside `backend/`.

## Setup — Frontend

1. `cd frontend`
2. `npm install`
3. `cp .env.example .env` (default `VITE_API_URL=http://localhost:8000` is
   correct for local dev against the backend above)
4. `npm run dev`
5. App is live at `http://localhost:5173`

## Environment variables

| Variable | Where | Required | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | backend | yes | Gemini API key from Google AI Studio |
| `GEMINI_MODEL` | backend | no | defaults to `gemini-2.5-flash` |
| `DATABASE_URL` | backend | no | defaults to local SQLite; set to your Postgres URL in production |
| `VITE_API_URL` | frontend | yes | URL of the deployed backend |

## Deployment

- **Backend → Render:** new Web Service from this repo, root directory
  `backend`, build command `pip install -r requirements.txt`, start command
  `uvicorn main:app --host 0.0.0.0 --port $PORT`. Add a free Render Postgres
  instance and set `DATABASE_URL` to its connection string, plus
  `GEMINI_API_KEY`.
- **Frontend → Vercel:** import this repo, root directory `frontend`,
  framework preset "Vite". Set `VITE_API_URL` to your Render backend URL.

## Live links

- Frontend: (https://clinical-reviewer-ten.vercel.app)

## Known limitations

See `docs/TECHNICAL_DECISIONS.md` for the full list — short version: no
auth, upload MIME type is trusted rather than signature-verified, and the
free hosting tier means the first request after idle time is slow
(cold start).
