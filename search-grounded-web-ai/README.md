🔍 Search-Grounded AI Assistant (RAG)

A search-grounded AI assistant that answers user questions using real-time web data, reducing hallucinations by grounding responses in verifiable sources.

This project demonstrates a Retrieval-Augmented Generation (RAG) architecture using Tavily for web search and an LLM for controlled reasoning.

🚀 Features

🔎 Real-time web search using Tavily Search API

🧠 RAG architecture (Retrieve → Augment → Generate)

💬 Conversational memory (multi-turn context)

📊 Confidence score for each answer

⚠️ Uncertainty & assumptions section

🔗 Transparent source citations

🤖 Suggested follow-up questions (agent-like behavior)

🎨 Clean, recruiter-friendly UI

🛡️ Reduced hallucinations by design

🧠 Architecture Overview
User (Browser)
   ↓
Flask Web App (Server)
   ↓
Tavily Web Search (Retrieval)
   ↓
Context Builder (Augmentation)
   ↓
LLM (Generation)
   ↓
Answer + Sources + Confidence


This system does not rely on the LLM’s internal knowledge alone.
Instead, it grounds every answer in live web data.

🔁 Why RAG?

Large Language Models have:

Static training data

Knowledge cutoffs

Finite context windows

By using Retrieval-Augmented Generation, this app:

Fetches fresh, relevant information

Limits hallucinations

Improves trust and explainability

🛠️ Tech Stack

Backend: Python, Flask

Retrieval: Tavily Search API

LLM: OpenRouter (OpenAI-compatible API)

Frontend: HTML, CSS (vanilla)

State: Flask session (chat memory)

No heavy frameworks (LangChain, React) — everything is explicit and explainable.

📂 Project Structure
.
├── app.py                # Flask backend
├── templates/
│   └── index.html        # UI
├── .env                  # API keys
├── requirements.txt
└── README.md

⚙️ Setup Instructions
1️⃣ Clone the repository
git clone https://github.com/your-username/search-grounded-ai
cd search-grounded-ai

2️⃣ Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add environment variables (.env)
TAVILY_API_KEY=your_tavily_key
OPENROUTER_API_KEY=your_openrouter_key

5️⃣ Run the app
python app.py


Open: http://127.0.0.1:5000

🧪 Example Query

User: Who won yesterday’s India vs Pakistan cricket match?

AI Answer:

India won by 61 runs

Confidence: High (0.90)

Sources: Economic Times, The Hindu, Indian Express

🔐 Security & Safety Notes

LLM outputs plain text only (no HTML rendering)

UI escapes content safely

API keys stored via environment variables

Designed for demo / portfolio use (not production)

📌 What This Project Demonstrates

Practical use of RAG (not just theory)

Controlled LLM reasoning

Explainable AI outputs

End-to-end system design

Real-world AI engineering patterns

🧩 Future Improvements

Deployment (Render / Railway)

Streaming responses

Source sentence highlighting

Feedback loop (thumbs up/down)

Caching frequent queries

👤 Author

Aadhidharmar T
B.Tech AI & Data Science
Focused on practical ML, RAG systems, and AI product engineering

⭐ Final Note

This project focuses on trust, grounding, and explainability, not just generation — reflecting how real-world AI systems are built.