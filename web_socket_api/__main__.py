import asyncio
import logging
from threading import Thread

from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from web_socket_api.notification.connection_manager import ConnectionManager

from web_socket_api.notification.notifier import Notifier


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
connection_manager = ConnectionManager()
notifier = Notifier(
    connection_manager=connection_manager
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Web Socket Maromba</title>
    </head>
    <body>
        <h1>Web Socket Marombinha</h1>
       <span id="connection_id"></span>
       <br>
       <span id="websocket_state"></span>
        
        <ul id='messages'></ul>
        <script>
            function connectWS1(event) {
                let connectionId = new Date().getTime().toString();
                let spanConnectionId = document.getElementById("connection_id");
                spanConnectionId.textContent = "Esse é o meu connection id: " + connectionId;
                
                var ws = new WebSocket("ws://localhost:8000/ws/deployment_status/" + connectionId);
                ws.addEventListener('open', (event) => {
                    console.log('WebSocket Connected!');
                    let span = document.getElementById("websocket_state");
                    span.textContent = "🥳 - Web Socket está online!";
                    span.style.color = "green";
                });
                ws.onmessage = function(event) {
                    console.log('Received Message!');
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                ws.onclose = (event) => {
                    let span = document.getElementById("websocket_state");
                    span.textContent = "🫠 - Web Socket está offine!";
                    span.style.color = "red";
                    console.log('Closed Web Socket!');
                };
                event.preventDefault()
            }
            window.onload = connectWS1
        </script>
    </body>
</html>
"""

@app.websocket("/ws/{channel}/{user_id}")
async def websocket_endpoint(channel: str, user_id: str, websocket: WebSocket):
    await connection_manager.connect(channel=channel, user_id=user_id, connection=websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(channel=channel, user_id=user_id)


@app.get("/")
async def get():
    return HTMLResponse(html)

def start_message_processing():
    asyncio.run(notifier.setup())

# Inicializa a thread para processar as mensagens da fila SQS
thread = Thread(target=start_message_processing, daemon=True)
thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
