from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import uuid
from datetime import datetime

# 🔥 IMPORTANTE: pega aquí tu URL de MongoDB Atlas
MONGO_URL = "mongodb+srv://Admin:<db_password>@minidc.skngkjh.mongodb.net/?appName=MiniDc"

client = MongoClient(MONGO_URL)
db = client["minidc"]
rooms_db = db["rooms"]
messages_db = db["messages"]

app = FastAPI()

# CORS (para evitar errores)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guardar conexiones activas
rooms_connections = {}

# -----------------------------
# CREAR SALA
# -----------------------------
@app.post("/create_room")
def create_room(name: str, creator: str):
    room_id = str(uuid.uuid4())[:8]

    room = {
        "room_id": room_id,
        "name": name,
        "creator": creator,
        "created_at": datetime.utcnow()
    }

    rooms_db.insert_one(room)

    return {
        "room_id": room_id,
        "link": f"https://minidc.onrender.com/join/{room_id}"
    }

# -----------------------------
# LISTAR MENSAJES
# -----------------------------
@app.get("/messages/{room_id}")
def get_messages(room_id: str):
    msgs = list(messages_db.find({"room_id": room_id}))
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs

# -----------------------------
# WEBSOCKET (CHAT)
# -----------------------------
@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    await websocket.accept()

    if room_id not in rooms_connections:
        rooms_connections[room_id] = []

    rooms_connections[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            msg_data = {
                "room_id": room_id,
                "username": username,
                "message": data,
                "time": str(datetime.utcnow())
            }

            # Guardar en MongoDB
            messages_db.insert_one(msg_data)

            # Enviar a todos
            for connection in rooms_connections[room_id]:
                await connection.send_text(f"{username}: {data}")

    except WebSocketDisconnect:
        rooms_connections[room_id].remove(websocket)

# -----------------------------
# ROOT (para evitar 404)
# -----------------------------
@app.get("/")
def root():
    return {"status": "Servidor activo 🚀"}
