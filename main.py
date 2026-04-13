from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

clients = {}

@app.get("/")
def home():
    return {"status": "Servidor activo 🚀"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    name = await websocket.receive_text()
    clients[websocket] = name

    # Avisar que alguien entró
    for client in clients:
        await client.send_text(f"🟢 {name} se unió")

    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                await client.send_text(f"{name}: {data}")

    except WebSocketDisconnect:
        del clients[websocket]
        for client in clients:
            await client.send_text(f"🔴 {name} salió")
