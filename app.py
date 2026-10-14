from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import os

app = FastAPI()
connections = set()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Touch & Vibe ❤️</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: radial-gradient(circle, #46165f, #10051c);
    color: white;
    font-family: Arial, sans-serif;
}
h1 {
    color: #ff8bd5;
    text-shadow: 0 0 18px #ff1493;
}
#heart {
    border: none;
    background: transparent;
    font-size: 125px;
    cursor: pointer;
    animation: beat 1s infinite;
    touch-action: manipulation;
}
@keyframes beat {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.12); }
}
#status { color: #ffd2ed; }
</style>
</head>
<body>
    <h1>Touch & Vibe</h1>
    <button id="heart" aria-label="Touch heart">❤️</button>
    <p id="status">Connecting...</p>

<script>
const statusText = document.getElementById("status");
const heart = document.getElementById("heart");

let socket;

function connect() {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";

    socket = new WebSocket(
        protocol + "//" + location.host + "/ws"
    );

    socket.onopen = () => {
        statusText.textContent = "Connected ❤️";
    };

    socket.onmessage = (event) => {
        if (event.data === "touch") {
            if (navigator.vibrate) {
                navigator.vibrate(300);
            }
            heart.animate(
                [
                    { transform: "scale(1)" },
                    { transform: "scale(1.3)" },
                    { transform: "scale(1)" }
                ],
                { duration: 350 }
            );
        }
    };

    socket.onclose = () => {
        statusText.textContent = "Reconnecting...";
        setTimeout(connect, 2000);
    };

    socket.onerror = () => {
        statusText.textContent = "Connection problem";
    };
}

heart.addEventListener("click", () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send("touch");
    }
});

connect();
</script>
</body>
</html>
"""

@app.get("/")
async def home():
    return HTMLResponse(HTML)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            if message == "touch":
                for client in list(connections):
                    if client != websocket:
                        try:
                            await client.send_text("touch")
                        except Exception:
                            connections.discard(client)

    except WebSocketDisconnect:
        connections.discard(websocket)

    except Exception:
        connections.discard(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
