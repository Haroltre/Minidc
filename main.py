from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir todo (importante)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Usuarios y salas
users = {}  # username: password
rooms = {}  # room: [websockets]
messages = {}  # room: [mensajes]


@app.get("/")
def home():
    return {"status": "ok"}


# 🧑 Registro
@app.post("/register")
async def register(data: dict):
    username = data["username"]
    password = data["password"]

    if username in users:
        return {"success": False, "msg": "Usuario ya existe"}

    users[username] = password
    return {"success": True}


# 🔑 Login
@app.post("/login")
async def login(data: dict):
    username = data["username"]
    password = data["password"]

    if users.get(username) == password:
        return {"success": True}
    return {"success": False}


# 💬 WebSocket
@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(ws: WebSocket, room: str, username: str):
    await ws.accept()

    if room not in rooms:
        rooms[room] = []
        messages[room] = []

    rooms[room].append(ws)

    # enviar historial
    for msg in messages[room]:
        await ws.send_text(msg)

    try:
        while True:
            data = await ws.receive_text()
            msg = f"{username}: {data}"

            messages[room].append(msg)

            for client in rooms[room]:
                await client.send_text(msg)

    except WebSocketDisconnect:
        rooms[room].remove(ws)
