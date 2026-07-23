# AI Charlotte - Personal RAG Chatbot

**Copyright (c) 2025 Charlotte Qazi | Created and maintained by Charlotte Qazi | Licensed under the MIT License**

A production-ready chatbot that answers questions about Charlotte Qazi's professional background, experience, and skills using Retrieval-Augmented Generation (RAG).

Here's a blog on how I built it - [Building AI-Charlotte: How to build a RAG chatbot in a day](https://charlotteqazi.medium.com/building-ai-charlotte-how-to-build-a-rag-chatbot-in-a-day-8e924ae50ef6)

> **Setting up with your own CV?** See [DEV_SETUP.md](./DEV_SETUP.md) for extra detail (chunking options, GitHub/Medium pipelines, tests).

## Quick Start

Local setup needs **four things** working together: Python deps (in a venv), env vars, Supabase tables, and a populated Qdrant collection. Skipping any of these is the usual reason chat fails.

### Prerequisites
- Python 3.9+ (3.10+ recommended; Railway uses 3.12)
- Node.js 18+ and npm 9+
- Accounts/keys: OpenAI, Qdrant Cloud, Supabase

### 1. Installation
```bash
git clone YOUR_GITHUB_REPO_URL ai-charlotte
cd ai-charlotte

# Backend — always use this venv for Python commands
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

> **Important:** Activate the venv in every terminal before running backend or CLI commands (`source .venv/bin/activate`). System `python3` will not see packages like `openai` and will fail with `ModuleNotFoundError`.

### 2. Environment Configuration
```bash
cp .env.example .env
```

Fill in `.env` (all of these are required for a working local app):

```bash
# OpenAI — embeddings + chat + moderation
OPENAI_API_KEY=your-openai-key

# Qdrant — vector search
QDRANT_URL=https://YOUR-CLUSTER.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-key
QDRANT_COLLECTION=ai_charlotte

# Supabase — users, message limits, chat history
# URL must match your project ref exactly: https://<project-ref>.supabase.co
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Frontend → local backend (use your Railway URL only in production)
VITE_API_URL=http://127.0.0.1:8000
```

Notes:
- `SUPABASE_URL` must match the `ref` in your Supabase JWT. A typo causes DNS errors (`nodename nor servname provided`).
- Restart the backend after editing `.env` (uvicorn `--reload` does not reliably pick up env changes).
- There is **no stub/demo mode** for users: missing Supabase credentials will stop the backend from starting correctly.

> **Next:** create Supabase tables ([Database Setup](#database-setup-supabase)), then index documents ([Index documents into Qdrant](#3-index-documents-into-qdrant)).

### 3. Index documents into Qdrant

A new Qdrant cluster has **no collections**. Chat retrieval will fail or return empty context until you embed documents.

With the venv active:

```bash
source .venv/bin/activate

# Chunk source files
python -m backend.cli.process_cv data/raw/cv.md
python -m backend.cli.process_qa data/raw/q-and-a.md

# Embed + upsert (uses QDRANT_COLLECTION from .env)
python -m backend.cli.embed_and_upsert \
  --input data/processed/cv_chunks.jsonl \
  --recreate-collection

python -m backend.cli.embed_and_upsert \
  --input data/processed/q-and-a_qa_chunks.jsonl
```

You should see a point count in the CLI output (e.g. 22 points after CV + Q&A). That collection name must match `QDRANT_COLLECTION` in `.env`.

### 4. Start the Application
```bash
# Terminal 1: Backend (venv required)
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

On backend startup you want to see Supabase initialized successfully (not credential warnings).

### 5. Use the Chatbot
- **Web Interface**: Visit `http://localhost:5173`
- **API**: `http://127.0.0.1:8000` (health: `GET /health`)

Complete onboarding in the UI first so a user row exists in Supabase, then chat.
## Example Queries

Try asking Charlotte's chatbot:

**About Professional Experience:**
- "What is Charlotte's experience at BCG?"
- "What are Charlotte's technical skills?"
- "Tell me about Charlotte's AI projects"
- "What leadership experience does Charlotte have?"

**About Blog Content & Insights:**
- "What are your thoughts on building Gen AI for humans?"
- "What did you learn at Google Women Developer Academy?"
- "Why is accessibility important in development?"
- "What impact does coding have on mental health?"

**General Questions:**
- "How did Charlotte transition into tech?"
- "Has Charlotte given any presentations?"

## Database Setup (Supabase)

The onboarding system uses Supabase to store user data and manage sessions. Follow these steps to set up your database:

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in/up
2. Click "New Project"
3. Choose your organization
4. Fill in project details:
   - **Name**: `ai-charlotte` (or your preferred name)
   - **Database Password**: Generate a strong password and save it
   - **Region**: Choose closest to your users
5. Click "Create new project"

### 2. Get Your Credentials

Once your project is created:

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://abcdefgh.supabase.co`)
   - **Anon/Public Key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
   - **Service Role Key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`) - **IMPORTANT**: This bypasses RLS

### 3. Create the Users Table

In your Supabase dashboard, go to **SQL Editor** and run:

```sql
-- Create users table for onboarding flow
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    interests TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0
);

-- Add RLS (Row Level Security) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (for onboarding)
CREATE POLICY "Allow anonymous user creation" ON users
    FOR INSERT TO anon
    WITH CHECK (true);

-- Allow reading user data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT TO anon
    USING (true);

-- Allow updating message count (for rate limiting)
CREATE POLICY "Allow message count updates" ON users
    FOR UPDATE TO anon
    USING (true);

-- Create messages table for chat history
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    sender TEXT NOT NULL CHECK (sender IN ('user', 'agent')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS policies for messages
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Allow inserting messages
CREATE POLICY "Allow message creation" ON messages
    FOR INSERT TO anon
    WITH CHECK (true);

-- Allow reading messages
CREATE POLICY "Allow reading messages" ON messages
    FOR SELECT TO anon
    USING (true);
```

### 4. Test Database Connection

```bash
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

In another terminal:

```bash
curl -X POST http://127.0.0.1:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "interests": "Testing the onboarding flow"
  }'
```

Expected response:
```json
{
  "user_id": "1b8ea2e1-f0d0-4b25-9511-9c56778aeb7d"
}
```

### 5. Verify in Supabase Dashboard

1. Go to **Table Editor** → **users**
2. You should see your test user in the table
3. Check that all fields are populated correctly

## API Usage

### User Creation Endpoint
```bash
curl -X POST "http://127.0.0.1:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "interests": "I am a recruiter looking at Charlotte for a senior developer role"}'
```

Response:
```json
{
  "user_id": "a6bc8110-e5f8-4ab1-b579-af45badb6b83"
}
```

### Chat Endpoint
```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Charlotte'\''s experience at BCG?"}'
```

Response:
```json
{
  "answer": "Charlotte has been working as a Senior AI Engineer at BCG X...",
  "sources": [
    {
      "title": "",
      "url": null,
      "score": 0.48140544
    }
  ]
}
```

### Health Check
```bash
curl -s http://127.0.0.1:8000/health | jq .
```

## Testing the RAG System

### Run Comprehensive Evaluation
```bash
source .venv/bin/activate

# Test the current CV in data/raw/ (automatic discovery)
pytest tests/test_current_cv.py -v -s

# Full RAG system evaluation
pytest tests/test_rag_evaluation.py -v -s

# Test Medium blog integration
pytest tests/test_medium_integration.py -v -s

# Test specific components
pytest tests/test_rag_evaluation.py::TestRAGEvaluation::test_individual_questions -v -s
```

### Expected Performance
The RAG system typically achieves:
- **Success Rate**: 75-87% on CV-related questions
- **Response Time**: ~2 seconds average
- **Grade**: A-B (Good to Very Good)

Sample evaluation output:
```
🎯 RAG SYSTEM EVALUATION REPORT
============================================================
📊 Overall Performance:
   Success Rate: 75.0% (6/8)
   Average Score: 0.63/1.0
   Average Response Time: 2.00s

🎓 RAG System Grade: B (Good)
============================================================
```

## Project Architecture

### Backend (FastAPI)
- **`backend/main.py`**: FastAPI application entry point
- **`backend/api/routes.py`**: API endpoints including `/api/chat`
- **`backend/services/`**: RAG pipeline components
  - `rag_service.py`: Main RAG orchestration
  - `retrieval/`: Vector similarity search
  - `generation/`: LLM response generation
  - `chunking/`: CV content processing
- **`backend/cli/`**: Command-line tools for data processing

### Frontend (React + MUI)
- **Modern chat interface** built with Vite + TypeScript
- **Material-UI components** for clean, responsive design
- **Real-time messaging** with the RAG backend
- **Auto-proxy** to backend API (`/api/*` → `127.0.0.1:8000`)

### Data Pipeline
- **Raw CV**: `data/raw/cv.pdf` (Charlotte's CV)
- **Medium Blog**: Auto-processed from RSS feed (`@charlotteqazi`)
- **Processed Chunks**: `data/processed/` (semantic chunks from CV and blog posts)
- **Vector Database**: Qdrant collection with embedded chunks
- **Retrieval**: Semantic search for relevant context
- **Generation**: OpenAI GPT-3.5-turbo for responses

## RAG System Features

### ✅ Implemented
- **Generic CV Processing**: Handles multiple CV formats and styles
- **Medium Blog Integration**: Automatic RSS feed processing and chunking
- **Semantic Chunking**: Creates meaningful content boundaries for CVs and blog posts
- **Vector Retrieval**: Fast similarity search with Qdrant
- **Context-Aware Generation**: GPT-3.5-turbo with retrieved context
- **Comprehensive Testing**: Automated evaluation with grading
- **Production-Ready API**: FastAPI with proper error handling
- **Modern Frontend**: React chat interface with MUI

### 🎯 Performance Strengths
- **Experience Questions**: 100% success rate
- **Technical Skills**: High accuracy retrieval
- **Career Background**: Excellent context understanding
- **Fast Responses**: ~2 second average response time
- **Edge Case Handling**: Graceful unknown topic responses

### ⚠️ Known Limitations
- **Education Queries**: Lower success rate (identified via testing)
- **Specific Metrics**: Some detailed achievement numbers may be missed
- **Context Window**: Limited to retrieved chunk context

## Troubleshooting

### Common Issues

**`ModuleNotFoundError: No module named 'openai'` (or similar) when running CLI**
- You are not using the project venv. Run `source .venv/bin/activate` first.

**Backend crash / health 500 related to `Secure` / security headers**
- `secure` 0.3.x (Python 3.9) and 2.x (Python 3.10+) have different APIs. `backend/main.py` supports both.
- Local (3.9): `pip install 'secure==0.3.0'`
- Deploy (3.10+): pip installs `secure` 2.x automatically via `secure>=0.3.0`

**Moderation error: invalid model `text-moderation-latest`**
- OpenAI now expects `omni-moderation-latest` (see `backend/services/moderation/moderator.py`).

**Chat 404: `User session not found`**
- Supabase URL/key wrong or empty, or `users` table missing.
- Confirm backend log shows Supabase initialized (not stub/credential warnings).
- Complete onboarding again after fixing `.env` and restarting the backend.

**Supabase DNS / `nodename nor servname provided`**
- `SUPABASE_URL` typo. It must be `https://<project-ref>.supabase.co` matching Settings → API.

**`'QdrantClient' object has no attribute 'search'`**
- Current `qdrant-client` uses `query_points` (fixed in retrieval code). Reinstall deps from `requirements.txt` if needed.

**"No relevant contexts" / empty or weak answers**
- Collection missing or empty, or `QDRANT_COLLECTION` does not match what you upserted into.
- Re-run the [Index documents into Qdrant](#3-index-documents-into-qdrant) steps.

**Port already in use**
```bash
# Kill existing processes
lsof -i :8000 -t | xargs kill -9  # Backend
lsof -i :5173 -t | xargs kill -9  # Frontend
```

**CORS errors**
- Ensure backend is running on `127.0.0.1:8000`
- Frontend automatically proxies API requests

**Poor response quality**
- Check API keys are configured correctly
- Run test suite to identify specific issues
- Review retrieved context quality

**Supabase connection issues**
- Ensure `SUPABASE_SERVICE_KEY` is set (not just `SUPABASE_ANON_KEY`)
- Check that the `users` and `messages` tables exist
- Verify RLS policies allow the required operations
- Look for initialization errors in server logs
- Restart uvicorn after changing `.env`

### Getting Help
1. Check terminal logs for error messages
2. Run health check: `curl -s http://127.0.0.1:8000/health`
3. Test individual components with pytest
4. See [DEV_SETUP.md](./DEV_SETUP.md) for detailed troubleshooting

## Technology Stack

- **Backend**: FastAPI, Python 3.9+, Pydantic
- **Frontend**: React 18, TypeScript, Material-UI, Vite
- **Database**: Supabase (PostgreSQL with real-time features)
- **AI/ML**: OpenAI GPT-3.5-turbo, text-embedding-3-small
- **Vector DB**: Qdrant Cloud
- **Testing**: pytest, requests
- **Development**: Hot reload, environment management

## Contributing

This is Charlotte's personal chatbot project. For setting up your own version:
1. See [DEV_SETUP.md](./DEV_SETUP.md) for complete setup instructions
2. Replace Charlotte's CV with your own
3. Customize test questions and system prompts
4. Adjust chunking parameters as needed

## License

This project is for educational and portfolio purposes. 

## Disclaimer

This project was created by Charlotte Qazi for learning and demonstration purposes.

You are welcome to fork and adapt it under the terms of the MIT license.  
However, please do **not upload other people's documents** (e.g., CVs) without explicit consent.

This project is intended for personal and responsible use only, such as exploring your own data, learning about RAG, or testing with non-sensitive content.

I take no responsibility for any misuse of this code or its components. If you choose to deploy or extend this project, you are solely responsible for ensuring it complies with relevant laws, platform policies, and ethical practices
