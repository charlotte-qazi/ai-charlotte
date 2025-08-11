## AI Charlotte - RAG Chatbot

Personal RAG chatbot backend and frontend.

### Backend (FastAPI)

- Create `.env` from `.env.example` and fill values
- Install dependencies:
  ```bash
  pip install fastapi uvicorn[standard] python-dotenv pydantic openai qdrant-client
  ```
- Run the API:
  ```bash
  uvicorn backend.main:app --reload
  ```
- Test endpoints:
  - Health: `GET /health`
  - Chat: `POST /api/chat` with body `{ "message": "Hello" }`

### Project Structure
- `backend/` FastAPI app and RAG modules
- `frontend/` React app (to be added)
- `data/` raw and processed documents 