from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

rooms = {}
users = {}
owners = {}
messages = {}

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(ws: WebSocket, room: str, username: str):
    await ws.accept()

    if room not in rooms:
        rooms[room] = []
        users[room] = []
        messages[room] = []
        owners[room] = username  # 👑 primer usuario es owner

    rooms[room].append(ws)
    users[room].append(username)

    # 📢 enviar historial
    for msg in messages[room]:
        await ws.send_text(msg)

    # 📢 enviar usuarios
    async def send_users():
        data = "USERS:" + ",".join(users[room])
        for client in rooms[room]:
            await client.send_text(data)

    await send_users()

    try:
        while True:
            data = await ws.receive_text()

            # 👑 comando kick
            if data.startswith("/kick "):
                target = data.replace("/kick ", "")
                if username == owners[room] and target in users[room]:
                    index = users[room].index(target)
                    client = rooms[room][index]
                    await client.close()
                    continue

            msg = f"{username}: {data}"
            messages[room].append(msg)

            for client in rooms[room]:
                await client.send_text(msg)

    except WebSocketDisconnect:
        if ws in rooms[room]:
            index = rooms[room].index(ws)
            rooms[room].remove(ws)
            users[room].remove(username)

        await send_users()
