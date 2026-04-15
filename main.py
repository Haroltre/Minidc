from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

rooms = {}
users = {}

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(ws: WebSocket, room: str, username: str):
    await ws.accept()

    if room not in rooms:
        rooms[room] = []
        users[room] = []

    rooms[room].append(ws)
    users[room].append(username)

    # 📢 enviar lista de usuarios
    async def send_user_list():
        data = "USERS:" + ",".join(users[room])
        for client in rooms[room]:
            await client.send_text(data)

    await send_user_list()

    try:
        while True:
            data = await ws.receive_text()
            msg = f"{username}: {data}"

            for client in rooms[room]:
                await client.send_text(msg)

    except WebSocketDisconnect:
        rooms[room].remove(ws)
        users[room].remove(username)
        await send_user_list()
