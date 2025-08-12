# How I built AI-Charlotte

**Copyright (c) 2025 Charlotte Qazi | Created and maintained by Charlotte Qazi | Licensed under the MIT License**

## Goal:

Build a personal chatbot using Retrieval-Augmented Generation (RAG) to answer questions with context from my CV, blog posts, GitHub, YouTube, and other personal content.

## Purpose:

- Learn how to build a modular, production-grade RAG system from scratch
- Use it as a portfolio piece and technical foundation for future CTO work
- Focus on understanding each component, not just plugging in templates


## Decisions:

### LLM provider

#### Decision: gpt-3.5-turbo

- Cost-effective: GPT-3.5 offers excellent performance for much lower cost than GPT-4.
- Easy to use and well-supported by ecosystem tools (LangChain, FastAPI, Cursor, etc.).
- High-quality embeddings from OpenAI work well with general-purpose personal data (CV, blog, etc.).

### Embedding model

#### Decision: OpenAI text-embedding-3-small

- High-quality semantic representations
- Compatible with GPT family
- Commercially supported
- Easy to integrate with Qdrant and Python stack

### Stack

#### Decision: FastAPI, React and MUI

- Personal familiarity
- Sufficiently powerful to showcase developer talent
- Clean and easy to customise
- Integrates well with Python-based AI tools (OpenAI, Qdrant, etc.)
- FastAPI: Clean, modern async Python web framework, easy to scale, test, and structure modularly
- React is a flexible, widely supported frontend framework
- MUI provides clean, production-quality components out of the box for fast iteration and professional looking styling

### Chunking Strategy

#### Decision: Semantic chunking via MD file

- Moved from fixed size (1200 chars) overlapping (200 chars) chunking as chunks covered too many topics due to strict chunk size
- Semantic chunking from a markdown file creates logical breaks at sections and content boundaries
