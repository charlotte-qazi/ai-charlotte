# Development Setup Guide

This guide walks you through setting up the AI Charlotte RAG chatbot from scratch with your own CV and environment configuration.

## Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm 9+
- **OpenAI API key** (for embeddings and chat completion)
- **Qdrant Cloud account** (or local Qdrant instance)
- **Your CV** in PDF or Markdown format

## 1. Initial Project Setup

### Clone and Setup Repository
```bash
git clone YOUR_GITHUB_REPO_URL ai-charlotte
cd ai-charlotte

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Starter code is on branch: starter-code
git checkout starter-code
```

### Get Required Credentials

To run the full RAG system, you'll need API keys from two services. This takes about 10-15 minutes to set up.

#### 1. OpenAI API Key (Required)
OpenAI provides the language model (GPT-3.5-turbo) and text embeddings for the RAG system.

**Step-by-step:**
1. **Visit OpenAI Platform**: Go to [platform.openai.com](https://platform.openai.com)
2. **Create Account**: Sign up or log in to your OpenAI account
3. **Add Payment Method**: 
   - Go to "Billing" in the left sidebar
   - Add a payment method (credit card required)
   - Add initial credits ($5-10 recommended for testing)
4. **Generate API Key**:
   - Navigate to "API Keys" in the left sidebar
   - Click "Create new secret key"
   - Give it a name like "AI Charlotte RAG"
   - Copy the key (starts with `sk-...`)
   - ⚠️ **Save this immediately** - you won't be able to see it again

**Cost Estimate**: ~$0.50-2.00 for typical development/testing usage

#### 2. Qdrant Cloud Account (Required)
Qdrant provides the vector database for storing and searching document embeddings.

**Step-by-step:**
1. **Visit Qdrant Cloud**: Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. **Create Account**: Sign up with email or GitHub
3. **Create a Cluster**:
   - Click "Create Cluster"
   - Choose "Free Tier" (1GB storage, perfect for CVs)
   - Select a region (closest to you for best performance)
   - Give it a name like "ai-charlotte"
   - Click "Create"
4. **Get Connection Details**:
   - Wait for cluster to be ready (~2-3 minutes)
   - Click on your cluster name
   - Copy the **Cluster URL** (looks like: `https://xyz-abc.us-east4-0.gcp.cloud.qdrant.io:6333`)
   - Go to "API Keys" tab
   - Click "Create API Key"
   - Copy the API key

**Cost**: Free tier includes 1GB storage (sufficient for personal CV projects)


#### 3. Verify Your Credentials
Before proceeding, test that your credentials work:

**Test OpenAI:**
```bash
curl -H "Authorization: Bearer YOUR_OPENAI_KEY" \
  https://api.openai.com/v1/models
# Should return a list of available models
```

**Test Qdrant:**
```bash
curl -H "api-key: YOUR_QDRANT_API_KEY" \
  "YOUR_QDRANT_URL/collections"
# Should return an empty collections list: {"result":{"collections":[]}}
```

#### What You Should Have Now:
- ✅ OpenAI API key (starts with `sk-...`)
- ✅ Qdrant cluster URL (ends with `:6333`)
- ✅ Qdrant API key
- ✅ Both services tested and working

**Security Note**: Never commit these keys to version control. Keep them secure and rotate them periodically. Ensure that you include any .env files in .gitignore.

### Create Environment Configuration
```bash
# Create environment file from template
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Qdrant Configuration (Cloud)
QDRANT_URL=https://your-cluster.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION=ai_charlotte

# Alternative: Local Qdrant (uncomment if using local instance)
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=
```

## 2. Prepare Your CV

### CV Format Requirements
Your CV can be in either:
- **PDF format** (.pdf)
- **Markdown format** (.md)

### Place Your CV
```bash
# Create data directories if they don't exist
mkdir -p data/raw data/processed

# Copy your CV to the raw data directory
cp /path/to/your/cv.pdf data/raw/
# OR
cp /path/to/your/cv.md data/raw/
```

### CV Content Tips
For best results, ensure your CV includes clear sections:
- **Professional Experience** (with company names, roles, dates)
- **Education** (degrees, universities, dates)
- **Technical Skills** (programming languages, tools, frameworks)
- **Projects/Achievements** (key accomplishments, presentations)
- **Leadership Experience** (if applicable)

## 3. Process Your CV

### Run CV Processing
```bash
# Activate virtual environment
source .venv/bin/activate

# Process your CV (replace with your actual filename)
python -m backend.cli.process_cv data/raw/your-cv.pdf

# Or for Markdown CV
python -m backend.cli.process_cv data/raw/your-cv.md

# Verify the output
ls -la data/processed/
head -n 2 data/processed/your-cv_chunks.jsonl | jq .
```

### Expected Output
You should see:
- A JSONL file in `data/processed/` with your CV chunks
- Processing statistics (number of chunks, word counts, etc.)
- Each chunk should have meaningful headings and content

Example chunk:
```json
{
  "id": "your-cv-0",
  "chunk_index": 0,
  "text": "Senior Software Engineer at TechCorp...",
  "source": "your-cv",
  "heading": "Professional Experience",
  "chunk_type": "experience",
  "word_count": 95,
  "metadata": {
    "filename": "your-cv.pdf",
    "processing_method": "cv_chunker",
    "source_format": "pdf"
  }
}
```

## 4. Create Vector Embeddings

### Embed and Upload to Qdrant
```bash
# Generate embeddings and upload to vector database
python -m backend.cli.embed_and_upsert \
  --input data/processed/your-cv_chunks.jsonl \
  --collection ai_charlotte

# Verify upload success
# Check the logs for "Successfully upserted X points to collection ai_charlotte"
```

### Troubleshooting Embeddings
If you encounter issues:

**OpenAI API errors:**
```bash
# Test your OpenAI key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

**Qdrant connection errors:**
```bash
# Test Qdrant connection (replace with your URL)
curl -H "api-key: $QDRANT_API_KEY" \
  "$QDRANT_URL/collections"
```

## 5. Start the Application

### Start Backend Server
```bash
# In terminal 1 - Backend
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Frontend Server
```bash
# In terminal 2 - Frontend
cd frontend
npm run dev
```

### Verify Setup
```bash
# In terminal 3 - Test endpoints
# Health check
curl -s http://127.0.0.1:8000/health | jq .

# Test chat with your CV
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "What is my professional experience?"}' | jq .
```

## 6. Add Your GitHub Repositories (Optional)

If you want to include your GitHub repositories in the RAG system:

### Setup GitHub Integration
```bash
# Add to your .env file:
GITHUB_USERNAME=your-github-username
GITHUB_API_TOKEN=your-github-personal-access-token
```

**Get GitHub Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `public_repo` scope (or `repo` for private repos)
3. Add the token to your `.env` file

### Process GitHub Repositories
```bash
# Ingest and chunk all your GitHub repositories
python -m backend.cli.process_github --output data/processed/github_chunks.jsonl

# Add to vector database
python -m backend.cli.embed_and_upsert --input data/processed/github_chunks.jsonl
```

**What gets indexed:**
- Repository metadata (languages, topics, stars, forks)
- README content from each repository
- Programming language statistics
- Project descriptions and URLs

**Example queries after setup:**
- "What programming languages does [NAME] use?"
- "Tell me about [NAME]'s React projects"
- "What are [NAME]'s most popular repositories?"

## 7. Add Your Medium Blog (Optional)

If you have a Medium blog, you can add your articles to the RAG system:

### Process Medium Blog Posts
```bash
# Activate environment
source .venv/bin/activate

# Process your Medium blog posts (replace @username with your Medium username)
python -m backend.cli.process_medium @username

# Or use the full RSS URL
python -m backend.cli.process_medium https://medium.com/feed/@username

# Example with Charlotte's blog
python -m backend.cli.process_medium @charlotteqazi --max-posts 10
```

### Add Blog Posts to Vector Database
```bash
# Embed and add to vector database (adjust filename as needed)
python -m backend.cli.embed_and_upsert \
  --input data/processed/your-name_medium_chunks.jsonl \
  --collection ai_charlotte
```

### Medium RSS URL Format
- Your Medium RSS feed is always: `https://medium.com/feed/@yourusername`
- You can also just provide `@yourusername` and the tool will convert it automatically
- The tool will fetch your latest posts, clean the content, and chunk them appropriately

### Troubleshooting Medium Import
If you encounter SSL errors:
```bash
# Test your Medium RSS feed manually
curl -s "https://medium.com/feed/@yourusername" | head -20

# The tool uses proper SSL verification by default for security
# If you need to bypass SSL in development (NOT recommended for production):
export VERIFY_SSL=false
python -m backend.cli.process_medium @yourusername

# For production, always keep SSL verification enabled (default)
unset VERIFY_SSL  # or export VERIFY_SSL=true
```

**SSL Configuration:**
- **Production**: SSL verification is enabled by default using system certificates
- **Development**: Can be disabled via `VERIFY_SSL=false` environment variable
- **Security**: Never disable SSL verification in production environments

## 8. Test Your RAG System

### Run Comprehensive Tests
```bash
# Activate environment
source .venv/bin/activate

# Test your specific CV (automatically detects CV in data/raw/)
pytest tests/test_current_cv.py -v -s

# Run RAG evaluation tests
pytest tests/test_rag_evaluation.py -v -s

# Run CV chunking tests
pytest tests/test_cv_chunker.py -v -s

# Run all tests
pytest tests/ -v
```

**What the current CV test validates:**
- ✅ **Automatic CV Discovery**: Finds your CV in `data/raw/` regardless of filename
- ✅ **File Accessibility**: Ensures CV is readable and has content
- ✅ **Chunking Quality**: Tests that your CV chunks appropriately (2+ chunks, reasonable sizes)
- ✅ **Content Coverage**: Validates professional content (experience, skills, education)
- ✅ **CLI Processing**: Tests the complete `process_cv` command with your CV
- ✅ **Embedding Compatibility**: Ensures chunks work with OpenAI embeddings
- ✅ **End-to-End RAG**: Tests the complete pipeline with generic questions

**Example output:**
```
✅ Found CV: my-resume.pdf
   Format: pdf
   Size: 245,832 bytes

✅ CV chunking successful:
   Chunks: 8
   Average words: 89.3
   Chunk types: {'experience', 'skills', 'education'}
   Sample headings: ['Professional Experience', 'Technical Skills', 'Education']
```

### Customize Test Questions
Edit `tests/test_rag_evaluation.py` to include questions specific to your CV:

```python
# In the test_questions fixture, update questions like:
{
    "question": "What is [YOUR_NAME]'s experience at [YOUR_COMPANY]?",
    "category": "experience",
    "expected_keywords": ["[YOUR_COMPANY]", "[YOUR_ROLE]", "[KEY_SKILLS]"],
    "difficulty": "easy"
}
```

## 9. Customization Options

### Adjust Chunking Parameters
If you need different chunk sizes, modify `backend/services/chunking/cv_chunker.py`:
```python
class CVChunker:
    def __init__(self):
        self.target_words = 100  # Adjust target chunk size
        self.max_words = 150     # Adjust maximum chunk size
        self.min_words = 15      # Adjust minimum chunk size
```

### Customize System Prompts
Edit the system prompt in `backend/services/generation/generator.py`:
```python
SYSTEM_PROMPT = f"""You are an AI assistant representing {YOUR_NAME}, 
a {YOUR_PROFESSION} with expertise in {YOUR_EXPERTISE_AREAS}. 
Answer questions about {YOUR_NAME}'s background, experience, and skills 
based on the provided context."""
```

### Update Collection Name
If you want a different collection name:
1. Update `QDRANT_COLLECTION` in `.env`
2. Update the collection name in test files
3. Re-run the embedding process

## 10. Troubleshooting Common Issues

### "No relevant contexts found" Error
This means the retrieval system isn't finding matching content:
```bash
# Check if your collection exists and has data
curl -H "api-key: $QDRANT_API_KEY" \
  "$QDRANT_URL/collections/ai_charlotte"

# Re-run embedding if needed
python -m backend.cli.embed_and_upsert \
  --input data/processed/your-cv_chunks.jsonl \
  --collection ai_charlotte
```

### Poor Test Results
If your RAG evaluation shows low scores:
1. **Check chunk quality**: Review `data/processed/your-cv_chunks.jsonl`
2. **Verify embeddings**: Ensure all chunks were uploaded to Qdrant
3. **Adjust similarity threshold**: Lower `min_score` in `backend/api/routes.py`
4. **Improve CV structure**: Add clearer section headings and formatting

### Port Already in Use
```bash
# Kill processes using the ports
lsof -i :8000 -t | xargs kill -9  # Backend
lsof -i :5173 -t | xargs kill -9  # Frontend
```

## 11. Production Considerations

### Environment Security
- Never commit `.env` files to version control
- Use environment-specific configurations
- Rotate API keys regularly

### Performance Optimization
- Monitor OpenAI API usage and costs
- Consider caching frequently asked questions
- Implement rate limiting for production use

### Monitoring
- Set up logging for API requests
- Monitor Qdrant collection health
- Track RAG system performance metrics

## 12. Next Steps

Once your basic setup is working:
1. **Add more content**: Process additional documents (blog posts, projects)
2. **Improve prompts**: Customize system prompts for your specific use case
3. **Add features**: Implement conversation memory, source citations
4. **Deploy**: Set up production deployment with Docker
5. **Monitor**: Add analytics and performance monitoring

## Support

If you encounter issues:
1. Check the logs in both backend and frontend terminals
2. Verify all environment variables are set correctly
3. Test individual components (CV processing, embeddings, retrieval)
4. Run the test suite to identify specific problems
5. Review the main README.md for additional troubleshooting tips 