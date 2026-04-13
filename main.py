from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rooms = {}
messages = {}

@app.get("/")
def home():
    return {"status": "ok"}

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(ws: WebSocket, room: str, username: str):
    await ws.accept()

    if room not in rooms:
        rooms[room] = []
        messages[room] = []

    rooms[room].append(ws)

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
