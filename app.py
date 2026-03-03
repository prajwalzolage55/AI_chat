import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(mongo_uri)
db = client["Chatbot"]
collection = db["users"]

app=FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert AI engineer specialized in Agentic AI and ML."
     "You are helpful, creative, clever, and very friendly. "
     "You are created by Prajwal Zolage and your name is Rakhandar."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

# LLM Model
llm = ChatGroq(
    api_key=groq_api_key,
    model="openai/gpt-oss-20b"
)

chain = prompt | llm

user_id = "user1"

def get_history(user_id):
    chats = list(
        collection.find({"user_id": user_id})
        .sort("timestamp", -1)   # newest first
        .limit(6)                # 👈 ONLY last 6 messages
    )

    chats.reverse()  # keep correct order

    history = []

    for chat in chats:
        if chat["role"] == "user":
            history.append(HumanMessage(content=chat["message"]))
        elif chat["role"] == "assistant":
            history.append(AIMessage(content=chat["message"]))

    return history

@app.get("/", response_class=HTMLResponse)
def chat_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
def chat(request: ChatRequest):
    history = get_history(request.user_id)
    response = chain.invoke({"history": history, "input": request.message})
    collection.insert_one({
        "user_id": request.user_id,
        "role": "user",
        "message": request.message,
        "timestamp": datetime.utcnow()
        })

        # Store assistant message
    collection.insert_one({
        "user_id": request.user_id,
        "role": "assistant",
        "message": response.content,
        "timestamp": datetime.utcnow()
    })

    return {"response": response.content}
