from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import json
import sqlite3
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database (create the posts table if it doesn't exist)
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

# Call initialize_db() when the application starts
initialize_db()

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
        print(f"Broadcasted message: {message}")

manager = ConnectionManager()

# Post model
class Post(BaseModel):
    username: str
    content: str
    image_url: str = None
    timestamp: str

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket connection attempt received")
    await manager.connect(websocket)
    try:
        print("WebSocket connection established")
        with get_db_connection() as conn:
            posts = conn.execute("SELECT * FROM posts ORDER BY timestamp DESC LIMIT 20").fetchall()
            for post in reversed(posts):
                await websocket.send_text(json.dumps(dict(post)))
            print("Sent initial posts to client")

        while True:
            data = await websocket.receive_text()
            print(f"Received data from client: {data}")
            post_data = json.loads(data)
            post_data["timestamp"] = datetime.datetime.now().isoformat()
            
            with get_db_connection() as conn:
                conn.execute("INSERT INTO posts (username, content, image_url, timestamp) VALUES (?, ?, ?, ?)",
                             (post_data["username"], post_data["content"], post_data.get("image_url"), post_data["timestamp"]))
                conn.commit()
            print(f"Inserted new post into database: {post_data}")
            
            await manager.broadcast(json.dumps(post_data))
            print(f"Broadcasted new post to all clients")
    except WebSocketDisconnect:
        print("WebSocket connection closed by client")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)