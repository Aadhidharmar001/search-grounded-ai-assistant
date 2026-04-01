# Hybrid Memory-First Search-Grounded AI Assistant

A production-ready hybrid Retrieval-Augmented Generation (RAG) assistant that combines **semantic memory retrieval (EmbeddingGemma + FAISS)** with **real-time web search grounding (Tavily)** to generate structured, explainable answers using **LLaMA-3 via OpenRouter**.

Unlike traditional RAG systems that rely only on external retrieval, this assistant first checks a **local semantic memory layer** before performing live web search. This improves response speed, reduces repeated API calls, and enables persistent learning across sessions.

---

# Architecture Overview

The assistant follows a memory-first hybrid reasoning pipeline:


User Query
↓
EmbeddingGemma (semantic embedding)
↓
FAISS Vector Memory Search
↓
If match found → return stored answer instantly
Else
↓
Tavily Web Retrieval
↓
Context Builder
↓
LLaMA-3 Reasoning via OpenRouter
↓
Structured Response Generation
↓
Answer stored back into semantic memory


This enables:

- faster responses for repeated queries
- reduced hallucinations
- persistent assistant learning
- scalable retrieval architecture

---

# Features

## Semantic Memory Layer (NEW)

Uses:

- EmbeddingGemma (Google DeepMind embedding model)
- FAISS vector similarity index

Capabilities:

- detects similar past questions
- retrieves answers instantly
- reduces repeated web searches
- improves latency over time
- enables persistent assistant learning

---

## Real-time Web Search

Uses Tavily Search API for:

- up-to-date information retrieval
- citation-backed answers
- reliable external grounding

Ensures responses remain:

- accurate
- traceable
- current

---

## Structured LLM Reasoning

Powered by:

meta-llama/llama-3-8b-instruct (via OpenRouter)

Responses include:

- direct answer
- key points
- uncertainty disclosure
- cited sources

---

## Confidence Scoring

Answer reliability calculated using:

- number of retrieved sources
- search depth
- relevance scores

Displayed as:

Low / Medium / High confidence

---

## Conversational Memory

Maintains recent conversation history using Flask session storage.

Supports:

- multi-turn reasoning
- context-aware responses

---

## Agent-like Behavior

Assistant supports:

- semantic memory reuse
- web fallback retrieval
- structured reasoning
- persistent learning loop

Making it behave like a hybrid reasoning agent instead of a simple chatbot.

---

# Tech Stack

Backend:

Flask (Python)

Semantic Memory:

EmbeddingGemma (SentenceTransformers)
FAISS vector similarity index

Search Retrieval:

Tavily Web Search API

LLM Reasoning:

OpenRouter API  
(meta-llama/llama-3-8b-instruct)

Frontend:

Vanilla HTML/CSS/JS

Deployment:

Render / Railway / Heroku ready

---

# Quick Start

## Local Development

Clone repository:


git clone <repository-url>
cd search-grounded-web-ai


Create virtual environment:


python -m venv venv
source venv/bin/activate


Windows:


venv\Scripts\activate


Install dependencies:


pip install -r requirements.txt


Create environment variables:


cp .env.example .env


Edit `.env` file:


TAVILY_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
FLASK_SECRET_KEY=your_secret_here
FLASK_ENV=development


Run application:


python app.py


Visit:


http://localhost:5000


---

# Production Deployment

## Render Deployment

1. Connect repository to Render
2. Set build command:


pip install -r requirements.txt


3. Set start command:


gunicorn --bind 0.0.0.0:$PORT app:app


4. Add environment variables in dashboard

---

## Railway Deployment

1. Connect repository
2. Railway auto-detects Flask app
3. Add environment variables

---

# Environment Variables

Create `.env` file:


TAVILY_API_KEY=your_tavily_key
OPENROUTER_API_KEY=your_openrouter_key

FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=production

PORT=5000


---

# API Endpoints

Main interface:


GET / POST /


Health check endpoint:


GET /health


---

# Core Architecture Components

Web Retrieval Layer:

Tavily API integration with configurable search depth

Semantic Memory Layer:

EmbeddingGemma embeddings + FAISS vector index

Reasoning Engine:

LLaMA-3 via OpenRouter structured prompting

Conversation Memory:

Flask session-based context tracking

Confidence Scoring:

Multi-factor reliability estimation

Citation Mapping:

Source traceability support

Follow-up Generation:

Agent-style question suggestions

---

# Why This Architecture Matters

Traditional assistants:


query → web search → LLM response


This assistant:


query
→ semantic memory search
→ if miss → web search
→ reasoning
→ persistent storage


Benefits:

- faster responses
- reduced API usage
- scalable retrieval pipeline
- improved answer consistency
- agent-style learning behavior

---

# Monitoring

Health check endpoint:


/health


Supports:

deployment monitoring  
uptime verification  
service diagnostics  

---

# Security Features

Secure session configuration  
environment variable validation  
input sanitization  
production-safe cookie handling  

---

# Future Improvements

Streaming responses  
source sentence highlighting  
feedback loop integration  
vector database upgrade (Pinecone / Weaviate)  
multi-tool agent orchestration  

---

# Author

Aadhidharmar T  
B.Tech Artificial Intelligence & Data Science  

Focused on:

GenAI systems  
retrieval-augmented reasoning  
semantic memory architectures  
agent-based AI engineering  

---

# License

MIT License
✅ After pasting this

Do:

git add README.md
git commit -m "docs: upgraded README to reflect semantic memory architecture"
git push
