import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, Form, File, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
import sqlite3
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize FastAPI app
app = FastAPI()

# Mount the directory for serving images
app.mount("/post_images", StaticFiles(directory="src/image/post_image"), name="post_images")

# CORS Middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Ensure upload directory exists
UPLOAD_DIR = "src/image/post_image"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# SQLite database connection
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database tables
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

initialize_db()

# WebSocket Manager for handling connections
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

# Post model for receiving data
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

# Image upload endpoint
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

# User model for login/signup
class User(BaseModel):
    username: str
    email: str
    password: str

# Helper function to hash passwords
def hash_password(password: str):
    return pwd_context.hash(password)

# Helper function to verify hashed passwords
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Signup endpoint
@app.post("/signup")
async def signup(user: User):
    # Check if username or email already exists
    with get_db_connection() as conn:
        existing_user = conn.execute("SELECT * FROM users WHERE username = ? OR email = ?", 
                                     (user.username, user.email)).fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or Email already taken")

        # Hash password before storing it
        hashed_password = hash_password(user.password)

        # Store the user in the database
        conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                     (user.username, user.email, hashed_password))
        conn.commit()

    return {"success": True, "message": "Signup successful!"}

@app.post("/login")
async def login(user: User):
    # Check if the user exists in the database
    stored_user = users_db.get(user.username)
    if stored_user and pwd_context.verify(user.password, stored_user["password"]):
        return {"success": True, "message": "Login successful!"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")