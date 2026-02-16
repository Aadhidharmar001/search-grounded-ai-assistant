# Search-Grounded AI Assistant

A production-ready RAG (Retrieval-Augmented Generation) application that provides web-grounded AI answers with full transparency and conversational memory.

## Features

- **Real-time Web Search**: Uses Tavily API for current, relevant information
- **Conversational Memory**: Maintains context across multiple questions
- **Confidence Scoring**: Quantifies answer reliability based on sources and search depth
- **Structured Answers**: Clear, organized responses with direct answers, key points, and uncertainties
- **Source Transparency**: Clickable citations linking directly to source materials
- **Agent-like Behavior**: Suggests relevant follow-up questions to guide exploration
- **Production-Ready**: Secure configuration, health checks, and deployment support

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: OpenRouter API (Llama-3-8B-Instruct)
- **Search**: Tavily Web Search API
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **Deployment**: Ready for Render/Railway/Heroku

## Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd search-grounded-web-ai
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run locally**:
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000`

### Production Deployment

#### Render Deployment
1. Connect your GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. Add environment variables in Render dashboard

#### Railway Deployment
1. Connect repository to Railway
2. Railway auto-detects Flask app
3. Add environment variables in Railway dashboard

## Environment Variables

Create a `.env` file with:

```env
# Required API Keys
TAVILY_API_KEY=your_tavily_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secure_random_secret_key
FLASK_ENV=production  # or development

# Optional: Port (defaults to 5000)
PORT=5000
```

## API Endpoints

- `GET/POST /` - Main application interface
- `GET /health` - Health check for monitoring

## Architecture

### Core Components

1. **Web Search Layer**: Tavily API integration with configurable search depth
2. **AI Processing**: Structured prompt engineering for consistent responses
3. **Memory Management**: Flask sessions for conversation history
4. **Confidence Calculation**: Multi-factor scoring system
5. **Citation Mapping**: Regex-based source linking
6. **Follow-up Generation**: Rule-based question suggestions

### Security Features

- Secure session configuration
- Environment variable validation
- Input sanitization
- HTTPS enforcement in production

## Development

### Code Structure
```
search-grounded-web-ai/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Single-page UI
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

### Key Functions

- `search_web()` - Web search with depth configuration
- `calculate_confidence()` - Answer reliability scoring
- `parse_answer_with_citations()` - Citation highlighting
- `generate_followup_questions()` - Agent-like suggestions
- `ask_llm()` - Structured AI prompting with history

## Monitoring

- Health check endpoint: `/health`
- Structured logging (add as needed)
- Error handling with user-friendly messages

## Contributing

1. Follow existing code patterns
2. Add tests for new features
3. Update documentation
4. Ensure production readiness

## License

MIT License - see LICENSE file for details.