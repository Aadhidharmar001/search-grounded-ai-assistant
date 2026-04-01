from flask import Flask, render_template, request, session
from tavily import TavilyClient
from openai import OpenAI
from functools import wraps
import time
import os
import requests
from dotenv import load_dotenv

# NEW: semantic memory module
from memory import search_memory, add_memory

load_dotenv()

app = Flask(__name__)

# Production-ready configuration
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex()),
    SESSION_COOKIE_SECURE=os.getenv("FLASK_ENV") == "production",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=1800,
    DEBUG=os.getenv("FLASK_ENV") != "production"
)

# Simple rate limiter
request_counts = {}
RATE_LIMIT = 10
RATE_WINDOW = 60


def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr or "unknown"
        current_time = time.time()

        if client_ip not in request_counts:
            request_counts[client_ip] = []

        request_counts[client_ip] = [
            t for t in request_counts[client_ip]
            if current_time - t < RATE_WINDOW
        ]

        if len(request_counts[client_ip]) >= RATE_LIMIT:
            return render_template(
                "index.html",
                error="Rate limit exceeded. Please wait."
            ), 429

        request_counts[client_ip].append(current_time)
        return f(*args, **kwargs)

    return decorated_function


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MAX_HISTORY_LENGTH = 5


def search_web(query, search_depth="basic"):
    response = tavily.search(
        query=query,
        search_depth=search_depth,
        max_results=5
    )
    return response["results"]


def build_context(results):
    context = ""
    for i, r in enumerate(results, 1):
        context += f"[{i}] Source: {r['url']}\n"
        context += f"Content: {r['content']}\n\n"
    return context


def calculate_confidence(results, search_depth):

    num_sources = len(results)

    depth_multiplier = 1.2 if search_depth == "advanced" else 1.0

    source_confidence = min(num_sources / 5.0, 0.6)

    relevance_bonus = 0.0

    if results and 'score' in results[0]:
        avg_relevance = sum(
            r.get('score', 0) for r in results
        ) / len(results)

        relevance_bonus = min(avg_relevance * 0.4, 0.4)

    confidence = (source_confidence + relevance_bonus) * depth_multiplier
    confidence = min(confidence, 1.0)

    if confidence >= 0.8:
        label = "High"
    elif confidence >= 0.6:
        label = "Medium"
    else:
        label = "Low"

    return f"{label} – {confidence:.2f}"


def ask_llm(question, context, history=None):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a factual assistant that provides web-grounded answers.\n"
                "Answer ONLY using provided context.\n"
                "Structure response exactly as:\n\n"
                "DIRECT ANSWER:\n\n"
                "KEY POINTS:\n\n"
                "UNCERTAINTY/ASSUMPTIONS:\n\n"
                "SOURCES USED:\n"
            )
        }
    ]

    if history:
        for exchange in history[-MAX_HISTORY_LENGTH:]:
            messages.append({
                "role": "user",
                "content": exchange["question"]
            })
            messages.append({
                "role": "assistant",
                "content": exchange["answer"]
            })

    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion:\n{question}"
    })

    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=messages,
        temperature=0.1,
        max_tokens=1000
    )

    return response.choices[0].message.content


@app.route("/", methods=["GET", "POST"])
@rate_limit
def index():

    answer = None
    sources = []
    error = None
    confidence = None
    followup_questions = []

    if request.method == "POST":

        try:

            question = request.form.get("question", "").strip()

            if not question:
                error = "Question cannot be empty."

            elif len(question) > 500:
                error = "Question too long."

            else:

                # MEMORY CHECK FIRST
                memory_answer = search_memory(question)

                if memory_answer:

                    return render_template(
                        "index.html",
                        answer=memory_answer,
                        parsed_answer=memory_answer,
                        sources=[],
                        error=None,
                        confidence="High – 0.95 (semantic memory)",
                        citation_map={},
                        followup_questions=[]
                    )

                # Continue with Tavily search

                if 'chat_history' not in session:
                    session['chat_history'] = []

                search_depth = (
                    "advanced"
                    if len(question.split()) > 10
                    else "basic"
                )

                results = search_web(question, search_depth)

                context = build_context(results)

                history = session.get('chat_history', [])

                answer = ask_llm(question, context, history)

                # STORE INTO MEMORY
                add_memory(question, answer)

                session['chat_history'].append({
                    "question": question,
                    "answer": answer
                })

                session['chat_history'] = session['chat_history'][-MAX_HISTORY_LENGTH:]

                session.modified = True

                sources = [
                    r.get("url")
                    for r in results
                    if r.get("url")
                ]

                confidence = calculate_confidence(results, search_depth)

        except requests.exceptions.RequestException:

            error = "Search service unavailable."

        except Exception as e:

            print("LLM ERROR:", str(e))

            error = "AI service temporarily unavailable."

    return render_template(
        "index.html",
        answer=answer,
        parsed_answer=answer,
        sources=sources,
        error=error,
        confidence=confidence,
        citation_map={},
        followup_questions=followup_questions
    )


@app.route("/health")
def health_check():

    return {
        "status": "healthy",
        "timestamp": "2026-02-16T00:00:00Z"
    }


@app.errorhandler(404)
def not_found(error):

    return render_template(
        "index.html",
        error="Page not found"
    ), 404


@app.errorhandler(500)
def internal_error(error):

    return render_template(
        "index.html",
        error="Internal server error"
    ), 500


if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))

    debug = os.getenv("FLASK_ENV") != "production"

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        use_reloader=False
    )