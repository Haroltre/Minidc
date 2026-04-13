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

@app.get("/")
def home():
    return {"status": "MiniDC running"}

@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(ws: WebSocket, room_id: str, username: str):
    await ws.accept()

    if room_id not in rooms:
        rooms[room_id] = []

    rooms[room_id].append(ws)

    try:
        while True:
            data = await ws.receive_text()
            msg = f"{username}: {data}"

            for client in rooms[room_id]:
                await client.send_text(msg)

    except WebSocketDisconnect:
        rooms[room_id].remove(ws)
