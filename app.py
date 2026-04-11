import os
import uuid
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(mongo_uri)
db = client["Chatbot"]
messages_collection = db["messages"]
sessions_collection = db["sessions"]

# Flask App
app = Flask(__name__)
CORS(app)

# File upload config
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {
    "txt", "py", "js", "json", "csv", "md", "html", "css",
    "log", "xml", "yaml", "yml", "ts", "jsx", "tsx", "java",
    "c", "cpp", "h", "hpp", "rb", "go", "rs", "sql", "sh",
    "bat", "ps1", "env", "cfg", "ini", "toml"
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert AI engineer specialized in Agentic AI and ML."
     "You are helpful, creative, clever, and very friendly. "
     "You are created by Prajwal Zolage and your name is Rakhandar.\n"
     "IMPORTANT: The user has selected {language} as their preferred language. You MUST write your ENTIRE response natively in {language}."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

# Prompt for file analysis
file_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert AI engineer specialized in Agentic AI and ML."
     "You are helpful, creative, clever, and very friendly. "
     "You are created by Prajwal Zolage and your name is Rakhandar."
     "\n\nThe user has uploaded a file. Analyze it thoroughly and respond to their question about it."
     "\nIf no specific question is asked, provide a comprehensive analysis of the file contents."
     "\n\nIMPORTANT: The user has selected {language} as their preferred language. You MUST write your ENTIRE response natively in {language}."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "FILE NAME: {filename}\n\nFILE CONTENT:\n```\n{file_content}\n```\n\nUSER MESSAGE: {input}")
])

# LLM Model
llm = ChatGroq(
    api_key=groq_api_key,
    model="openai/gpt-oss-20b"
)

chain = prompt | llm
file_chain = file_prompt | llm


# ─── Helper Functions ───────────────────────────────────────────────

def get_history(user_id, session_id):
    """Get the last 6 messages for a user in a specific session."""
    chats = list(
        messages_collection.find({"user_id": user_id, "session_id": session_id})
        .sort("timestamp", -1)
        .limit(6)
    )
    chats.reverse()

    history = []
    for chat in chats:
        if chat["role"] == "user":
            history.append(HumanMessage(content=chat["message"]))
        elif chat["role"] == "assistant":
            history.append(AIMessage(content=chat["message"]))

    return history


def generate_session_title(message):
    """Generate a short title from the first message."""
    title = message.strip()
    if len(title) > 50:
        title = title[:47] + "..."
    return title


# ─── Routes ─────────────────────────────────────────────────────────

@app.route("/")
def chat_ui():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "user1")
    message = data.get("message", "")
    session_id = data.get("session_id")
    language = data.get("language", "en-US")
    lang_map = {"en-US": "English", "hi-IN": "Hindi", "mr-IN": "Marathi"}
    target_lang = lang_map.get(language, "English")


    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Create a new session if none provided
    if not session_id:
        session_id = str(uuid.uuid4())
        sessions_collection.insert_one({
            "session_id": session_id,
            "user_id": user_id,
            "title": generate_session_title(message),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })

    history = get_history(user_id, session_id)
    
    response = chain.invoke({
        "language": target_lang,
        "history": history, 
        "input": message
    })

    # Store user message
    messages_collection.insert_one({
        "user_id": user_id,
        "session_id": session_id,
        "role": "user",
        "message": message,
        "timestamp": datetime.utcnow()
    })

    # Store assistant message
    messages_collection.insert_one({
        "user_id": user_id,
        "session_id": session_id,
        "role": "assistant",
        "message": response.content,
        "timestamp": datetime.utcnow()
    })

    # Update session timestamp
    sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": {"updated_at": datetime.utcnow()}}
    )

    return jsonify({
        "response": response.content,
        "session_id": session_id
    })


@app.route("/upload", methods=["POST"])
def upload_file():
    user_id = request.form.get("user_id", "user1")
    message = request.form.get("message", "Analyze this file")
    session_id = request.form.get("session_id")
    language = request.form.get("language", "en-US")
    lang_map = {"en-US": "English", "hi-IN": "Hindi", "mr-IN": "Marathi"}
    target_lang = lang_map.get(language, "English")

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not supported. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}), 400

    filename = secure_filename(file.filename)

    try:
        file_content = file.read().decode("utf-8", errors="replace")
    except Exception as e:
        return jsonify({"error": f"Could not read file: {str(e)}"}), 400

    # Truncate very large files
    max_chars = 15000
    truncated = False
    if len(file_content) > max_chars:
        file_content = file_content[:max_chars]
        truncated = True

    # Create a new session if none provided
    if not session_id:
        session_id = str(uuid.uuid4())
        sessions_collection.insert_one({
            "session_id": session_id,
            "user_id": user_id,
            "title": f"📎 {filename}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })

    history = get_history(user_id, session_id)

    actual_input = message
    if truncated:
        actual_input += "\n\n(Note: File was truncated to first 15,000 characters due to length.)"

    response = file_chain.invoke({
        "language": target_lang,
        "history": history,
        "filename": filename,
        "file_content": file_content,
        "input": actual_input
    })

    # Store user message with file reference
    user_msg = f"📎 **{filename}**\n\n{message}"
    messages_collection.insert_one({
        "user_id": user_id,
        "session_id": session_id,
        "role": "user",
        "message": user_msg,
        "timestamp": datetime.utcnow()
    })

    # Store assistant message
    messages_collection.insert_one({
        "user_id": user_id,
        "session_id": session_id,
        "role": "assistant",
        "message": response.content,
        "timestamp": datetime.utcnow()
    })

    # Update session timestamp
    sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": {"updated_at": datetime.utcnow()}}
    )

    return jsonify({
        "response": response.content,
        "session_id": session_id
    })


@app.route("/sessions", methods=["GET"])
def get_sessions():
    user_id = request.args.get("user_id", "user1")
    sessions = list(
        sessions_collection.find({"user_id": user_id})
        .sort("updated_at", -1)
        .limit(50)
    )

    result = []
    for s in sessions:
        result.append({
            "session_id": s["session_id"],
            "title": s.get("title", "Untitled"),
            "created_at": s["created_at"].isoformat(),
            "updated_at": s["updated_at"].isoformat()
        })

    return jsonify(result)


@app.route("/sessions/new", methods=["POST"])
def create_session():
    data = request.get_json()
    user_id = data.get("user_id", "user1")

    session_id = str(uuid.uuid4())
    sessions_collection.insert_one({
        "session_id": session_id,
        "user_id": user_id,
        "title": "New Chat",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    return jsonify({"session_id": session_id, "title": "New Chat"})


@app.route("/sessions/<session_id>", methods=["GET"])
def get_session_messages(session_id):
    user_id = request.args.get("user_id", "user1")
    messages = list(
        messages_collection.find({"user_id": user_id, "session_id": session_id})
        .sort("timestamp", 1)
    )

    result = []
    for m in messages:
        result.append({
            "role": m["role"],
            "message": m["message"],
            "timestamp": m["timestamp"].isoformat()
        })

    return jsonify(result)


@app.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    user_id = request.args.get("user_id", "user1")

    sessions_collection.delete_one({"session_id": session_id, "user_id": user_id})
    messages_collection.delete_many({"session_id": session_id, "user_id": user_id})

    return jsonify({"status": "deleted"})


# ─── Run ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
