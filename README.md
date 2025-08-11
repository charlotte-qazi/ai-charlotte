# AI Charlotte - RAG Chatbot

A personal chatbot project using a modular Retrieval-Augmented Generation (RAG) backend (FastAPI) and a simple React + MUI frontend.

This repo is scaffolded to learn and iterate quickly toward a production-ready RAG system.

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm 9+
- (Optional for later) Qdrant Cloud account and API key

### 1) Clone the repository
Replace the URL below with your GitHub repo URL.

```bash
git clone YOUR_GITHUB_REPO_URL ai-charlotte
cd ai-charlotte
```

### 2) Backend setup (FastAPI)
- Create and activate a virtual environment, install dependencies, and set up environment variables.

```bash
# From repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env from the example
cp .env.example .env
# Fill in values as needed (OpenAI/Qdrant). For now, mock chat works without keys.
```

- Start the backend server

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- Test the backend endpoints in a separate terminal

```bash
# Health check
curl -s http://127.0.0.1:8000/health | jq .

# Mock chat (returns a placeholder answer)
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hello!"}' | jq .
```

Notes:
- The RAG services under `backend/services/` are placeholders for ingestion, chunking, embeddings, vector store, retrieval, and generation.
- Environment variables are read from `.env` via `python-dotenv` (see `backend/core/config.py`).

### 3) Frontend setup (React + Vite + MUI)
- Install dependencies and start the dev server:

```bash
cd frontend
npm install
npm run dev
```

- Open the app at `http://127.0.0.1:5173`
- Type a message and you should see a mock answer returned from the backend.

The Vite dev server proxies `/api/*` to the FastAPI backend on `127.0.0.1:8000` (see `frontend/vite.config.ts`). Ensure the backend is running first.

### 4) Data ingestion (PDF processing)
Process your documents into text chunks for the RAG pipeline.

- **Place your PDF** in the `data/raw/` directory (e.g., `data/raw/cv.pdf`)
- **Run the ingestion CLI** to chunk the PDF into JSONL format:

```bash
# From repo root, with backend venv activated
source .venv/bin/activate

# Process PDF into chunks
python -m backend.cli.process_pdf \
  --input data/raw/cv.pdf \
  --output data/processed/cv_chunks.jsonl \
  --max-chars 1200 \
  --overlap-chars 200 \
  --source-label "cv"

# Check the output
ls -la data/processed/
wc -l data/processed/cv_chunks.jsonl
head -n 2 data/processed/cv_chunks.jsonl | jq .
```

**CLI Options:**
- `--input`: Path to input PDF file
- `--output`: Path to output JSONL file (default: `data/processed/cv_chunks.jsonl`)
- `--max-chars`: Maximum characters per chunk (default: 1200)
- `--overlap-chars`: Overlap between chunks (default: 200)
- `--source-label`: Label to attach to chunks (default: "cv")

**Output format:** Each line in the JSONL contains:
```json
{
  "id": "cv-0",
  "chunk_index": 0,
  "text": "...chunk content...",
  "source": "cv",
  "metadata": {
    "filename": "cv.pdf",
    "path": "data/raw/cv.pdf"
  }
}
```

### 5) Testing commands

**Smoke tests (basic functionality):**
- Backend:
  - Health: `curl -s http://127.0.0.1:8000/health`
  - Chat: `curl -s -X POST http://127.0.0.1:8000/api/chat -H 'Content-Type: application/json' -d '{"message": "Test"}'`
- Frontend:
  - Browser: visit `http://127.0.0.1:5173` and send a message
  - CLI (simple check server is up): `curl -I http://127.0.0.1:5173`

**Integration tests (PDF parsing quality):**
```bash
# Install pytest if not already installed
source .venv/bin/activate
pip install -r requirements.txt

# Basic PDF parsing test (structure and chunking)
pytest tests/integration/test_pdf_parsing.py -v -s

# Advanced PDF quality test (requires Markdown reference)
# Place your CV Markdown file at: data/raw/cv.md
# Then run the quality comparison test:
pytest tests/integration/test_pdf_quality.py -v -s

# Run all tests
pytest tests/ -v
```

**PDF parsing tests validate:**
- ✅ Text extraction from PDF pages
- ✅ Chunking quality and size limits  
- ✅ JSONL output structure and content
- ✅ Content quality (whitespace ratio, overlap)
- ✅ **Text similarity against reference** (character/word level)
- ✅ **Content completeness** (missing content detection)
- ✅ **Extraction accuracy metrics** (length/word count ratios)

## Project structure
- `backend/` FastAPI app and RAG modules
  - `backend/main.py` FastAPI entrypoint
  - `backend/api/routes.py` API routes (includes `POST /api/chat`)
  - `backend/schemas/` Pydantic models
  - `backend/core/config.py` env config loader
  - `backend/services/` placeholders for RAG components (ingestion, chunking, embedding, vector store, retrieval, generation)
- `frontend/` React app (Vite + TypeScript + MUI) with a simple chat UI
- `data/` raw and processed documents (empty placeholders for now)
- `.env.example` sample environment file
- `requirements.txt` backend Python dependencies

## Environment variables
Edit `.env` with the following variables when implementing the real RAG pipeline:

```bash
OPENAI_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION=personal_docs
```

For the current mock chat, these are not required.

## Troubleshooting
- Port in use:
  - Backend: `lsof -i :8000 -t | xargs kill -9`
  - Frontend: `lsof -i :5173 -t | xargs kill -9`
- CORS: The frontend dev server proxies `/api` to `127.0.0.1:8000`. Ensure backend is running locally and reachable.
- Python env: Always `source .venv/bin/activate` before running backend commands.
- Node version: Use Node 18+; `node -v`

## Roadmap (next steps)
- ✅ Implement PDF ingestion and chunking for CV
- Add OpenAI embeddings and Qdrant upsert
- Build retrieval + prompt construction  
- Replace mock `/api/chat` with real RAG pipeline output
- Add ingestion for Medium blog posts, GitHub, LinkedIn, YouTube
- Add tests (unit + integration) and Docker setup 