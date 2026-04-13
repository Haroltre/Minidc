from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir conexiones
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
    return {"status": "ok"}

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(ws: WebSocket, room: str, username: str):
    await ws.accept()

    if room not in rooms:
        rooms[room] = []

    rooms[room].append(ws)

    try:
        while True:
            data = await ws.receive_text()

            message = f"{username}: {data}"

            for client in rooms[room]:
                await client.send_text(message)

    except WebSocketDisconnect:
        rooms[room].remove(ws)
