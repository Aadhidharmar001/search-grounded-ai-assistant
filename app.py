from flask import Flask, render_template, request, session
from tavily import TavilyClient
from openai import OpenAI

import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Configuration for chat history
MAX_HISTORY_LENGTH = 5  # Keep last 5 exchanges

def search_web(query, search_depth="basic"):
    response = tavily.search(
        query=query,
        search_depth=search_depth,
        max_results=5  # Increased for better confidence scoring
    )
    return response["results"]

def build_context(results):
    context = ""
    for i, r in enumerate(results, 1):
        context += f"[{i}] Source: {r['url']}\n"
        context += f"Content: {r['content']}\n\n"
    return context

def calculate_confidence(results, search_depth):
    """
    Calculate confidence score based on:
    - Number of sources (more sources = higher confidence)
    - Search depth (advanced > basic)
    - Average relevance score if available
    """
    num_sources = len(results)
    depth_multiplier = 1.2 if search_depth == "advanced" else 1.0

    # Base confidence from number of sources (0-0.6)
    source_confidence = min(num_sources / 5.0, 0.6)

    # Relevance bonus if available (0-0.4)
    relevance_bonus = 0.0
    if results and 'score' in results[0]:
        avg_relevance = sum(r.get('score', 0) for r in results) / len(results)
        relevance_bonus = min(avg_relevance * 0.4, 0.4)

    confidence = (source_confidence + relevance_bonus) * depth_multiplier
    confidence = min(confidence, 1.0)

    # Convert to descriptive label
    if confidence >= 0.8:
        label = "High"
    elif confidence >= 0.6:
        label = "Medium"
    else:
        label = "Low"

    return f"{label} – {confidence:.2f}"

def parse_answer_with_citations(answer, sources):
    """
    Parse the answer to highlight cited sentences and map them to sources.
    Returns: (parsed_html, citation_map)
    """
    import re

    # Find all citations in the answer like [1], [2], etc.
    citation_pattern = r'\[(\d+)\]'
    citations_found = set()

    # Extract all unique citation numbers
    for match in re.finditer(citation_pattern, answer):
        citations_found.add(int(match.group(1)))

    # Create citation map (citation number -> source URL)
    citation_map = {}
    for i, source_url in enumerate(sources, 1):
        if i in citations_found:
            citation_map[i] = source_url

    # Replace citations with highlighted spans
    def replace_citation(match):
        citation_num = int(match.group(1))
        if citation_num in citation_map:
            return f'<span class="citation" data-source="{citation_map[citation_num]}" title="Source: {citation_map[citation_num]}">[{citation_num}]</span>'
        return match.group(0)

    parsed_answer = re.sub(citation_pattern, replace_citation, answer)

    return parsed_answer, citation_map

def generate_followup_questions(question, answer, sources):
    """
    Generate 2-3 relevant follow-up questions based on the current Q&A
    """
    followup_suggestions = []

    # Simple rule-based suggestions based on question type and content
    question_lower = question.lower()
    answer_lower = answer.lower()

    if any(word in question_lower for word in ['what is', 'explain', 'how does', 'what are']):
        followup_suggestions.append("Can you give me more details about this?")
        followup_suggestions.append("What are the main applications of this?")
        followup_suggestions.append("How has this evolved over time?")

    elif any(word in question_lower for word in ['who', 'person', 'people']):
        followup_suggestions.append("What are their major achievements?")
        followup_suggestions.append("What's their background?")
        followup_suggestions.append("How did they get started?")

    elif any(word in question_lower for word in ['when', 'date', 'year']):
        followup_suggestions.append("What led up to this event?")
        followup_suggestions.append("What were the consequences?")
        followup_suggestions.append("How did this change things?")

    elif any(word in question_lower for word in ['where', 'location', 'place']):
        followup_suggestions.append("What's the significance of this location?")
        followup_suggestions.append("What can you tell me about the surroundings?")
        followup_suggestions.append("How has this place changed?")

    else:
        followup_suggestions.append("Can you elaborate on this?")
        followup_suggestions.append("What are the key implications?")
        followup_suggestions.append("Are there any related topics I should know about?")

    # Return first 3 suggestions
    return followup_suggestions[:3]

def ask_llm(question, context, history=None):
    # Build conversation history
    messages = [
        {
            "role": "system",
            "content": (
                "You are a factual assistant that provides web-grounded answers. "
                "Always respond in this exact structure:\n\n"
                "DIRECT ANSWER: [1-2 sentences]\n\n"
                "KEY POINTS:\n- [bullet point]\n- [bullet point]\n\n"
                "UNCERTAINTY/ASSUMPTIONS:\n[List any uncertainties or assumptions made]\n\n"
                "SOURCES USED:\n[Cite sources by number, e.g., [1], [2]]\n\n"
                "Answer strictly using the provided context. "
                "If the answer is not in the context, say you don't know."
            )
        }
    ]

    # Add conversation history if available
    if history:
        for exchange in history[-MAX_HISTORY_LENGTH:]:
            messages.append({"role": "user", "content": exchange["question"]})
            messages.append({"role": "assistant", "content": exchange["answer"]})

    # Add current question with context
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
def index():
    answer = None
    sources = []
    error = None
    confidence = None
    parsed_answer = None
    citation_map = {}
    followup_questions = []

    if request.method == "POST":
        try:
            question = request.form.get("question")

            if not question:
                error = "Question cannot be empty."
            else:
                # Initialize session history if not exists
                if 'chat_history' not in session:
                    session['chat_history'] = []

                # Determine search depth based on question complexity
                search_depth = "advanced" if len(question.split()) > 10 else "basic"

                results = search_web(question, search_depth)
                context = build_context(results)

                # Get conversation history
                history = session.get('chat_history', [])

                answer = ask_llm(question, context, history)

                # Store this exchange in history
                session['chat_history'].append({
                    "question": question,
                    "answer": answer
                })
                # Keep only last N exchanges
                session['chat_history'] = session['chat_history'][-MAX_HISTORY_LENGTH:]
                session.modified = True

                sources = [r.get("url") for r in results if r.get("url")]
                confidence = calculate_confidence(results, search_depth)

                # Parse answer for citations
                parsed_answer, citation_map = parse_answer_with_citations(answer, sources)

                # Generate follow-up questions
                followup_questions = generate_followup_questions(question, answer, sources)

        except requests.exceptions.RequestException:
            error = "Search service is unavailable. Please try again later."
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

    return render_template(
        "index.html",
        answer=answer,
        parsed_answer=parsed_answer,
        sources=sources,
        error=error,
        confidence=confidence,
        citation_map=citation_map,
        followup_questions=followup_questions
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") != "production"

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        use_reloader=False
    )


