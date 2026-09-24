# Technical Decisions

## Why FastAPI for the backend

Python has the deepest ecosystem for AI/ML integration (the official Gemini
SDK, PDF/image tooling), and FastAPI adds async support, automatic request
validation via Pydantic, and free interactive API docs (`/docs`) with very
little boilerplate — useful both for building this quickly and for
demonstrating the API to a reviewer.

## Why React (Vite) for the frontend

React is the most widely supported option for a UI built from small pieces
of state (form, loading, error, report view, history), and Vite keeps the
dev/build setup minimal. Vercel deploys a Vite app with effectively zero
configuration.

## Why PostgreSQL (with SQLite for local dev)

Postgres is a sensible default for a persisted, structured record like a
clinical report — a JSON column for the flexible detailed report, ordinary
columns for status/timestamps that need to be queried and sorted. SQLAlchemy
is used as the ORM specifically so the same model code works against SQLite
locally (zero setup) and Postgres in production (`DATABASE_URL` swaps the
backend, including handling the `postgres://` vs `postgresql://` prefix
difference between how some hosts hand out the URL and what the driver
expects).

## Why Gemini for the AI/ML layer

The assignment requires handling typed, scanned, *and* handwritten
documents, across text, image, and PDF inputs. Rather than building a
separate OCR step (e.g. Tesseract) and feeding its output to a text-only
LLM — which compounds OCR mistakes into extraction mistakes, and typically
handles handwriting poorly — this project sends the raw document directly
to a multimodal model that reads images and PDFs natively. That reduces
pipeline complexity (fewer moving parts, fewer failure points) and tends to
produce better results on messy, real-world-style documents. Gemini
specifically was picked over closed alternatives because Google AI Studio
provides a genuine free API tier, which matters for a student project with
no budget.

## Important trade-offs

- **One AI call vs. a multi-step pipeline** — a single call producing both
  the summary and the detailed report is simpler and cheaper, at the cost
  of less independent control over summary quality. Acceptable for this
  assignment's scope; a natural extension is a two-step pipeline (extract
  structured fields first, then generate the summary from those fields).
- **No dedicated OCR step** — usually simpler and more accurate on
  handwriting, but means document-understanding quality depends entirely on
  the model provider, with less visibility/control than a self-hosted OCR
  step would give.
- **SQLite locally / Postgres in production** — convenient for local
  development, but means local testing never fully exercises
  Postgres-specific behavior.
- **Free-tier hosting (Render + Vercel)** — Render's free web service sleeps
  after inactivity, so the first request after a period of idleness will be
  slow (cold start, ~30-50s). Acceptable for an assignment demo, not for a
  real production deployment.
- **No DB migrations** — the schema is created via
  `Base.metadata.create_all()` rather than a migration tool like Alembic.
  Fine at this scope; would switch to Alembic for anything longer-lived.

## Known weaknesses / limitations

- No authentication — anyone with the URL can submit documents and see all
  reports. Fine for a demo, not for real clinical data.
- No automated test suite beyond what the assignment asks for (the main
  flow, plus a few validation-layer failure cases).
- Upload content-type validation trusts the browser-supplied MIME type
  rather than inspecting the file's actual signature ("magic bytes").
- The single retry on AI failure is a plain fixed retry, not
  backoff-based.
- CORS is wide open (`allow_origins=["*"]`) for ease of development —
  should be locked to the deployed frontend's exact origin before/at
  submission.

## What I would improve with more time

- Add basic auth so reports are scoped to a user/session.
- Move to a two-step AI pipeline (extract → summarize) for tighter control
  over report quality independent of extraction quality.
- Add file-signature validation instead of trusting the browser's MIME
  type.
- Add exponential backoff for AI-call retries.
- Move off free-tier hosting to avoid cold starts.
