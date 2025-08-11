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

### 4) Data ingestion (CV processing)
Process your CV into semantic chunks optimized for RAG retrieval.

- **Place your CV** in the `data/raw/` directory (supports PDF and Markdown)
- **Run the CV processing CLI** with generic chunking:

```bash
# From repo root, with backend venv activated
source .venv/bin/activate

# Process CV (PDF or Markdown) with generic CV chunking
python -m backend.cli.process_cv data/raw/cv.pdf

# Or process Markdown CV
python -m backend.cli.process_cv data/raw/cv.md

# Check the output (auto-generated in data/processed/)
ls -la data/processed/
wc -l data/processed/cv_chunks.jsonl
head -n 2 data/processed/cv_chunks.jsonl | jq .

# Embed chunks and upsert to Qdrant (requires OpenAI and Qdrant credentials in .env)
python -m backend.cli.embed_and_upsert \
  --input data/processed/cv_chunks.jsonl \
  --collection ai_charlotte
```

**Generic CV chunking features:**
- ✅ **Section-aware processing**: Detects experience, education, skills, achievements
- ✅ **Multiple CV formats**: Works with academic, creative, executive, entry-level CVs
- ✅ **Smart text cleaning**: Handles PDF artifacts, table formatting, whitespace
- ✅ **Semantic chunking**: Creates meaningful chunks based on content structure
- ✅ **Flexible input**: Supports both PDF and Markdown formats

**CLI Usage:**
```bash
python -m backend.cli.process_cv <input_file> [--output <output_file>]
```

**Options:**
- `input_file`: Path to CV (PDF or Markdown)
- `--output`: Output JSONL path (optional, auto-generated if not specified)

**Output format:** Each line in the JSONL contains:
```json
{
  "id": "cv-0",
  "chunk_index": 0,
  "text": "...semantic chunk content...",
  "source": "cv",
  "heading": "Professional Experience",
  "chunk_type": "experience",
  "word_count": 95,
  "metadata": {
    "filename": "cv.pdf",
    "processing_method": "cv_chunker",
    "source_format": "pdf"
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

**RAG System Evaluation (comprehensive chatbot testing):**
```bash
# Install test dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Run comprehensive RAG evaluation (requires API server running)
pytest tests/test_rag_evaluation.py -v -s

# Test specific components
pytest tests/test_rag_evaluation.py::TestRAGEvaluation::test_individual_questions -v -s
pytest tests/test_rag_evaluation.py::TestRAGEvaluation::test_edge_cases -v -s
pytest tests/test_rag_evaluation.py::TestRAGEvaluation::test_response_quality_metrics -v -s

# Run chunking tests
pytest tests/test_cv_chunker.py -v -s
pytest tests/test_cv_formats.py -v -s

# Run all tests
pytest tests/ -v
```

**RAG evaluation tests validate:**
- ✅ **Question answering accuracy** (8 realistic CV questions)
- ✅ **Response quality metrics** (keyword matching, completeness, speed)
- ✅ **Edge case handling** (unknown topics, graceful fallbacks)
- ✅ **Performance by category** (experience, skills, education, leadership)
- ✅ **Performance by difficulty** (easy, medium, hard questions)
- ✅ **API health and structure** (response format, error handling)
- ✅ **Grading system** (A+ to D based on success rate and quality)

**Example RAG evaluation output:**
```
🎯 RAG SYSTEM EVALUATION REPORT
============================================================
📊 Overall Performance:
   Success Rate: 75.0% (6/8)
   Average Score: 0.63/1.0
   Keyword Match Rate: 0.61/1.0
   Average Response Time: 2.00s

🎓 RAG System Grade: B (Good)
============================================================
```

**CV Chunking tests validate:**
- ✅ **Generic CV processing** (works with different CV formats)
- ✅ **Section detection** (experience, education, skills, achievements)
- ✅ **Chunk quality** (appropriate sizes, meaningful boundaries)
- ✅ **Content preservation** (no loss of important information)
- ✅ **Metadata extraction** (headings, chunk types, word counts)

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
QDRANT_COLLECTION=ai_charlotte
```

For the current mock chat, these are not required. For embeddings and vector storage, you'll need:
- `OPENAI_API_KEY`: Your OpenAI API key for embeddings
- `QDRANT_URL`: Your Qdrant Cloud URL (e.g., `https://xyz.us-east4-0.gcp.cloud.qdrant.io:6333`)
- `QDRANT_API_KEY`: Your Qdrant Cloud API key

## Troubleshooting
- Port in use:
  - Backend: `lsof -i :8000 -t | xargs kill -9`
  - Frontend: `lsof -i :5173 -t | xargs kill -9`
- CORS: The frontend dev server proxies `/api` to `127.0.0.1:8000`. Ensure backend is running locally and reachable.
- Python env: Always `source .venv/bin/activate` before running backend commands.
- Node version: Use Node 18+; `node -v`

## Roadmap (next steps)
- ✅ Implement PDF ingestion and chunking for CV
- ✅ Add OpenAI embeddings and Qdrant upsert
- ✅ Build retrieval + prompt construction  
- ✅ Replace mock `/api/chat` with real RAG pipeline output
- ✅ Add comprehensive RAG system evaluation tests
- ✅ Generic CV chunking for multiple formats
- Add ingestion for Medium blog posts, GitHub, LinkedIn, YouTube
- Add Docker setup and deployment configuration
- Improve education content retrieval (identified via testing)
- Add conversation memory and context awareness 