from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
import secrets
import os

app = FastAPI()

# Each invitation link has its own private room.
rooms = {}

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Touch & Vibe ❤️</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: Arial, sans-serif;
    color: white;
    background:
        radial-gradient(ellipse at bottom, #32105c 0%, #10051f 50%, #02010b 100%);
}

.stars {
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        radial-gradient(2px 2px at 20px 30px, white, transparent),
        radial-gradient(1px 1px at 80px 110px, #ffb9ec, transparent),
        radial-gradient(2px 2px at 150px 70px, #b9d8ff, transparent),
        radial-gradient(1px 1px at 220px 160px, white, transparent),
        radial-gradient(2px 2px at 270px 40px, #ffb9ec, transparent);
    background-size: 300px 220px;
    animation: drift 30s linear infinite;
}

@keyframes drift {
    from { transform: translateY(0); }
    to   { transform: translateY(-220px); }
}

.card {
    position: relative;
    z-index: 2;
    width: min(90%, 420px);
    padding: 35px 22px;
    text-align: center;
    border: 1px solid rgba(255, 160, 230, .35);
    border-radius: 28px;
    background: rgba(24, 8, 43, .72);
    box-shadow: 0 0 40px rgba(255, 30, 170, .17);
    backdrop-filter: blur(12px);
}

h1 {
    color: #ffb6e7;
    text-shadow: 0 0 18px #ff28b8;
    letter-spacing: 2px;
}

.subtitle {
    color: #e8c9ff;
    font-size: 14px;
}

#heart {
    display: block;
    margin: 22px auto;
    padding: 0;
    border: none;
    outline: none;
    background: transparent;
    color: #ff278b;
    font-size: 125px;
    cursor: pointer;
    filter: drop-shadow(0 0 18px #ff168d);
    animation: beat 1.1s infinite;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}

@keyframes beat {
    0%, 100% { transform: scale(1); }
    15%      { transform: scale(1.13); }
    30%      { transform: scale(1); }
    45%      { transform: scale(1.09); }
}

button.action {
    border: 0;
    border-radius: 24px;
    padding: 13px 20px;
    margin-top: 12px;
    background: linear-gradient(90deg, #ff329b, #a747ff);
    color: white;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 0 18px rgba(255, 50, 170, .3);
}

#status {
    color: #ffc9ec;
    font-size: 14px;
    min-height: 20px;
    overflow-wrap: anywhere;
}

#invite {
    display: none;
    width: 100%;
    margin-top: 12px;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #b45bdc;
    background: #180b2a;
    color: white;
    overflow-wrap: anywhere;
    font-size: 12px;
}

#inviteLink {
    color: #ffc2eb;
    overflow-wrap: anywhere;
}

.hidden {
    display: none !important;
}
</style>
</head>

<body>
<div class="stars"></div>

<div class="card">
    <h1>Touch & Vibe</h1>
    <p class="subtitle">Two hearts. One little moment. ❤️</p>

    <div id="setup">
        <p class="subtitle">
            Create your private invitation and share it
            with your special person.
        </p>

        <button class="action" id="create">
            Create Private Link 💌
        </button>

        <div id="invite">
            <p>Your invitation link:</p>
            <a id="inviteLink" href="#"></a>
            <br>
            <button class="action" id="copy">
                Copy Invitation Link
            </button>
        </div>
    </div>

    <div id="heartArea" class="hidden">
        <button id="heart" aria-label="Send a heart">❤️</button>
        <p id="status">Connecting to your special person...</p>
        <p class="subtitle">
            Touch the heart to send a little love.
        </p>
    </div>
</div>

<script>
const path = location.pathname;
const roomMatch = path.match(/^\/r\/([A-Za-z0-9_-]+)$/);

const setup = document.getElementById("setup");
const heartArea = document.getElementById("heartArea");
const statusText = document.getElementById("status");
const heart = document.getElementById("heart");

let socket;
let retryTimer;

function showRoom() {
    setup.classList.add("hidden");
    heartArea.classList.remove("hidden");
}

async function createInvitation() {
    const button = document.getElementById("create");
    button.disabled = true;
    button.textContent = "Creating link...";

    try {
        const response = await fetch("/create-room", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Could not create invitation");
        }

        const data = await response.json();
        const link = location.origin + data.path;

        const box = document.getElementById("invite");
        const anchor = document.getElementById("inviteLink");

        anchor.href = link;
        anchor.textContent = link;
        box.style.display = "block";

        document.getElementById("copy").onclick = async () => {
            try {
                await navigator.clipboard.writeText(link);
                document.getElementById("copy").textContent =
                    "Copied! ❤️";
            } catch (e) {
                window.prompt("Copy your invitation link:", link);
            }
        };

        button.textContent = "Link Created ❤️";
    } catch (error) {
        button.disabled = false;
        button.textContent = "Try Again";
        alert("Could not create the link. Please try again.");
    }
}

document.getElementById("create").addEventListener(
    "click", createInvitation
);

function connectRoom(roomId) {
    const protocol =
        location.protocol === "https:" ? "wss:" : "ws:";

    socket = new WebSocket(
        protocol + "//" + location.host + "/ws/" + roomId
    );

    socket.onopen = () => {
        statusText.textContent = "Connected ❤️";
    };

    socket.onmessage = (event) => {
        if (event.data === "touch") {
            if ("vibrate" in navigator) {
                navigator.vibrate([120, 60, 180]);
            }

            heart.animate(
                [
                    { transform: "scale(1)" },
                    { transform: "scale(1.35)" },
                    { transform: "scale(1)" }
                ],
                { duration: 450 }
            );

            statusText.textContent = "A little love arrived! 💗";

            setTimeout(() => {
                if (socket && socket.readyState === WebSocket.OPEN) {
                    statusText.textContent = "Connected ❤️";
                }
            }, 1800);
        }
    };

    socket.onclose = () => {
        statusText.textContent = "Reconnecting...";
        clearTimeout(retryTimer);

        retryTimer = setTimeout(
            () => connectRoom(roomId), 3000
        );
    };

    socket.onerror = () => {
        statusText.textContent = "Connection problem. Retrying...";
    };
}

if (roomMatch) {
    showRoom();
    connectRoom(roomMatch[1]);

    heart.addEventListener("click", () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send("touch");
        } else {
            statusText.textContent =
                "Not connected yet. Please wait...";
        }
    });
}
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.post("/create-room")
async def create_room():
    room_id = secrets.token_urlsafe(24)
    rooms.setdefault(room_id, set())

    return JSONResponse({
        "path": f"/r/{room_id}"
    })


@app.get("/r/{room_id}", response_class=HTMLResponse)
async def room_page(room_id: str):
    return HTML


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    room = rooms.setdefault(room_id, set())
    room.add(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            if message == "touch":
                for client in list(room):
                    if client != websocket:
                        try:
                            await client.send_text("touch")
                        except Exception:
                            room.discard(client)

    except WebSocketDisconnect:
        room.discard(websocket)

    except Exception:
        room.discard(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
