from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import HTTPException
import sqlite3

app = FastAPI()

# ================= DB =================
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room TEXT,
    username TEXT,
    message TEXT
)
""")

conn.commit()

# ================= USERS =================

@app.post("/register")
def register(username: str, password: str):
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return {"status": "ok"}
    except:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

@app.post("/login")
def login(username: str, password: str):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# ================= WEBSOCKET =================

rooms = {}  # room -> [websockets]

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(websocket: WebSocket, room: str, username: str):
    await websocket.accept()

    if room not in rooms:
        rooms[room] = []

    rooms[room].append(websocket)

    # 📜 enviar historial
    cursor.execute("SELECT username, message FROM messages WHERE room=?", (room,))
    history = cursor.fetchall()

    for user, msg in history:
        await websocket.send_text(f"{user}: {msg}")

    # 🟢 notificar entrada
    for client in rooms[room]:
        await client.send_text(f"🟢 {username} entró a {room}")

    try:
        while True:
            data = await websocket.receive_text()

            # 💾 guardar mensaje
            cursor.execute(
                "INSERT INTO messages (room, username, message) VALUES (?, ?, ?)",
                (room, username, data)
            )
            conn.commit()

            # 📡 enviar a todos
            for client in rooms[room]:
                await client.send_text(f"{username}: {data}")

    except WebSocketDisconnect:
        rooms[room].remove(websocket)
        for client in rooms[room]:
            await client.send_text(f"🔴 {username} salió")
