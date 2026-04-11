<div align="center">
  
# 🤖 Rakhandar AI Engineer Assistant

*A premium, multi-lingual, voice-enabled AI ChatBot powered by Flask, LangChain, and Groq.*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Persisted_Memory-green.svg?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Orchestration-orange.svg)](https://langchain.com/)

</div>

---

## 🌟 Overview

**Rakhandar** is a sophisticated AI chat interface designed to serve as an expert AI/ML Engineering Assistant. Originally built with FastAPI, the application has been successfully migrated to a robust **Flask** backend with a visually stunning Vanilla JS frontend. 

It boasts a comprehensive suite of features including persistent chat sessions, context-aware file analysis, native voice interaction capabilities, and seamless multilingual support (English, Hindi, Marathi).

---

## ✨ Key Features

- **💬 Persistent Chat Sessions**: Automatically tracks your conversations using MongoDB. Chat history is neatly organized into sessions by date (Today, Yesterday, Older).
- **🗣️ Multi-Lingual Support**: Select your preferred language (English, Hindi, Marathi) from the frontend. The system securely injects this directly into the LLM system prompt so Rakhandar natively replies in your chosen tongue.
- **🎤 Native Voice Integration**: Talk to Rakhandar using your microphone via the browser's native Web Speech API. 
- **🔊 Text-to-Speech (TTS)**: Let the AI read its responses aloud! The system is customized to prioritize male voices with dedicated support for English, Hindi, and Marathi phonetics.
- **📎 File Analysis Engine**: Upload code files (`.py`, `.js`, `.json`) or documents (`.txt`, `.csv`, `.md`). The application truncates and securely embeds the file contents into the LLM context for live code review and file analysis.
- **💅 Premium UI/UX**: A dark-mode, glassmorphic UI featuring smooth CSS animations, typing indicators, highlighted code blocks (Highlight.js), markdown support, and quick "Copy to Clipboard" functionality.

---

## 🛠️ Technology Stack

**Backend System:**
- **Framework**: Flask & Flask-CORS
- **AI Orchestration**: LangChain (`ChatPromptTemplate`, `MessagesPlaceholder`)
- **LLM Provider**: Groq API (`openai/gpt-oss-20b` or equivalent)
- **Database**: MongoDB (via `pymongo`) handling `sessions` and `messages`

**Frontend System:**
- **Core**: Vanilla HTML5, CSS3, JavaScript (No heavy frontend frameworks)
- **Styling**: Custom CSS Variables, Glassmorphism, Micro-animations
- **Libraries**: `marked.js` (Markdown), `highlight.js` (Syntax Highlighting)

---

## 🚀 Getting Started

Follow these instructions to get the Rakhandar chatbot running on your local machine.

### 1. Prerequisites

- **Python 3.10+**
- **MongoDB**: A running local MongoDB instance (or MongoDB Atlas URI, defaulting to `mongodb://localhost:27017/`)
- **Groq API Key**: You need an active API key from [Groq](https://console.groq.com/).

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/prajwalzolage55/AI_chat.git
cd AI_chat

# Create and activate a Virtual Environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a strict `.env` file in the root directory to store your API keys and configuration:

```env
GROQ_API_KEY=your_groq_api_key_here
MONGO_URI=mongodb://localhost:27017/
```

### 4. Run the Application

Start the Flask development server:

```bash
python app.py
```

Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 📂 File Structure

```text
├── app.py                  # Main Flask application and API routes
├── requirements.txt        # Python dependency manifest
├── .env                    # Environment variables (Keys & URIs)
├── uploads/                # Short-term local storage for uploaded files
└── templates/
    └── index.html          # Core Frontend application housing UI & Logic
```

---

<div align="center">
  <p>Developed with ❤️ by <a href="https://portfolio-r7ct-seven.vercel.app">Prajwal Zolage</a> &middot; AI/ML Engineer</p>
</div>
