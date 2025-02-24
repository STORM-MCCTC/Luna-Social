import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Form, File, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
import sqlite3
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import os
from fastapi import UploadFile, File

app = FastAPI()

# Mount the directory for serving images
app.mount("/post_images", StaticFiles(directory="src/image/post_image"), name="post_images")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the upload directory exists
UPLOAD_DIR = "src/image/post_image"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Database setup
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def initialize_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                image_url TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()

initialize_db()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Post model
class Post(BaseModel):
    username: str
    content: str
    image_url: Optional[str] = None
    timestamp: str

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        with get_db_connection() as conn:
            posts = conn.execute("SELECT * FROM posts ORDER BY timestamp DESC LIMIT 20").fetchall()
            for post in reversed(posts):
                await websocket.send_text(json.dumps(dict(post)))

        while True:
            data = await websocket.receive_text()
            post_data = json.loads(data)
            post_data["timestamp"] = datetime.datetime.now().isoformat()

            with get_db_connection() as conn:
                conn.execute("INSERT INTO posts (username, content, image_url, timestamp) VALUES (?, ?, ?, ?)",
                             (post_data["username"], post_data["content"], post_data.get("image_url"), post_data["timestamp"]))
                conn.commit()

            await manager.broadcast(json.dumps(post_data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Generate a unique filename using UUID
    file_extension = os.path.splitext(file.filename)[1]  # Get the file extension
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_location = f"src/image/post_image/{unique_filename}"

    # Save the file
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())

    return {"image_url": f"/post_images/{unique_filename}"}
