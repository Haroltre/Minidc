from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

clients = []

@app.get("/")
def home():
    return {"status": "Servidor activo 🚀"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    name = await websocket.receive_text()

    try:
        while True:
            msg = await websocket.receive_text()
            for client in clients:
                await client.send_text(f"{name}: {msg}")

    except WebSocketDisconnect:
        clients.remove(websocket)
