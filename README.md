# AI Charlotte - Personal RAG Chatbot

A production-ready chatbot that answers questions about Charlotte Qazi's professional background, experience, and skills using Retrieval-Augmented Generation (RAG).

**🚀 Ready to run with Charlotte's CV already processed and indexed.**

> **Setting up with your own CV?** See [DEV_SETUP.md](./DEV_SETUP.md) for complete development setup instructions.

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm 9+

### 1. Installation
```bash
git clone YOUR_GITHUB_REPO_URL ai-charlotte
cd ai-charlotte

# Backend setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..
```

### 2. Environment Configuration
```bash
# Create environment file
cp .env.example .env
```

The app will run in demo mode without API keys, but for full functionality, add:
```bash
# Optional: For full RAG functionality
OPENAI_API_KEY=your-openai-key
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
QDRANT_COLLECTION=ai_charlotte
```

### 3. Start the Application
```bash
# Terminal 1: Start backend
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 4. Use the Chatbot
- **Web Interface**: Visit `http://localhost:5173`
- **API**: Send POST requests to `http://127.0.0.1:8000/api/chat`

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

## API Usage

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

**"No relevant contexts found"**
- Ensure environment variables are set correctly
- Check that Qdrant collection exists and has data
- Verify OpenAI API key is valid

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

### Getting Help
1. Check terminal logs for error messages
2. Run health check: `curl -s http://127.0.0.1:8000/health`
3. Test individual components with pytest
4. See [DEV_SETUP.md](./DEV_SETUP.md) for detailed troubleshooting

## Technology Stack

- **Backend**: FastAPI, Python 3.9+, Pydantic
- **Frontend**: React 18, TypeScript, Material-UI, Vite
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