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

    join_msg = f"🟢 {name} se unió"
    for client in clients:
        await client.send_text(join_msg)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{name}: {data}"
            
            for client in clients:
                await client.send_text(message)

    except WebSocketDisconnect:
        del clients[websocket]
        leave_msg = f"🔴 {name} salió"
        for client in clients:
            await client.send_text(leave_msg)
