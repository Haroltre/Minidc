from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pymongo import MongoClient
import os

app = FastAPI()

# 🔥 MongoDB
MONGO_URL = os.getenv("mongodb+srv://Admin:<db_password>@minidc.skngkjh.mongodb.net/?appName=MiniDc")
client = MongoClient(MONGO_URL)
db = client["minidc"]
rooms_db = db["rooms"]

# 🧠 memoria en vivo
rooms = {}
users = {}
owners = {}

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(ws: WebSocket, room: str, username: str):
    await ws.accept()

    # crear sala si no existe
    if room not in rooms:
        rooms[room] = []
        users[room] = []

        data = rooms_db.find_one({"room": room})

        if not data:
            rooms_db.insert_one({
                "room": room,
                "messages": [],
                "owner": username
            })
            owners[room] = username
        else:
            owners[room] = data["owner"]

    rooms[room].append(ws)
    users[room].append(username)

    # 📥 enviar mensajes guardados
    data = rooms_db.find_one({"room": room})
    if data:
        for msg in data["messages"]:
            await ws.send_text(msg)

    # 📢 actualizar usuarios
    async def send_users():
        msg = "USERS:" + ",".join(users[room])
        for client in rooms[room]:
            await client.send_text(msg)

    await send_users()

    try:
        while True:
            data_msg = await ws.receive_text()

            # 👑 KICK
            if data_msg.startswith("/kick "):
                target = data_msg.replace("/kick ", "")
                if username == owners[room]:
                    for i, u in enumerate(users[room]):
                        if u == target:
                            await rooms[room][i].close()
                    continue

            msg = f"{username}: {data_msg}"

            # 💾 guardar en Mongo
            rooms_db.update_one(
                {"room": room},
                {"$push": {"messages": msg}}
            )

            for client in rooms[room]:
                await client.send_text(msg)

    except WebSocketDisconnect:
        if ws in rooms[room]:
            i = rooms[room].index(ws)
            rooms[room].remove(ws)
            users[room].remove(username)

        await send_users()
