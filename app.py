from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import secrets
import os

app = FastAPI()
rooms = {}

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#08030d">
<link rel="manifest" href="/manifest.json">
<title>Touch & Vibe ❤️</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    overflow: hidden;
    font-family: Arial, sans-serif;
    color: white;
    background:
        radial-gradient(ellipse at 50% 110%, #50103d 0%, transparent 55%),
        radial-gradient(ellipse at 10% 10%, #25104c 0%, transparent 50%),
        #05030a;
}

#universe {
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
}

.star {
    position: absolute;
    width: 2px;
    height: 2px;
    border-radius: 50%;
    background: white;
    box-shadow: 0 0 8px #ffc8f1;
    animation: twinkle 2s infinite alternate;
}

@keyframes twinkle {
    from { opacity: .2; transform: scale(.7); }
    to { opacity: 1; transform: scale(1.7); }
}

.nebula {
    position: absolute;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    filter: blur(85px);
    opacity: .23;
    background: #b20cff;
    animation: nebulaMove 12s ease-in-out infinite alternate;
}

.nebula.one {
    top: 5%;
    left: -100px;
}

.nebula.two {
    right: -100px;
    bottom: 0;
    background: #ff147e;
    animation-delay: -5s;
}

@keyframes nebulaMove {
    from { transform: translate(0, 0) scale(1); }
    to { transform: translate(40px, -35px) scale(1.3); }
}

.screen {
    position: relative;
    z-index: 2;
    min-height: 100vh;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.card {
    width: min(100%, 410px);
    padding: 34px 23px;
    text-align: center;
    border: 1px solid rgba(255, 151, 221, .3);
    border-radius: 28px;
    background: rgba(15, 7, 25, .78);
    backdrop-filter: blur(18px);
    box-shadow:
        0 0 35px rgba(255, 28, 150, .12),
        inset 0 0 30px rgba(150, 50, 255, .05);
    animation: cardAppear 1s ease;
}

@keyframes cardAppear {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

.eyebrow {
    color: #ff9dd9;
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
}

h1 {
    font-size: clamp(27px, 7vw, 38px);
    margin: 18px 0 12px;
    line-height: 1.25;
    background: linear-gradient(90deg, #fff, #ff9edb, #c6a0ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    filter: drop-shadow(0 0 15px rgba(255, 65, 177, .2));
}

.subtitle {
    color: #d5c1e9;
    font-size: 14px;
    line-height: 1.8;
}

.small-heart {
    font-size: 47px;
    margin: 18px 0;
    display: inline-block;
    filter: drop-shadow(0 0 15px #ff2c9c);
    animation: heartbeat 1.3s infinite;
}

@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    15% { transform: scale(1.15); }
    30% { transform: scale(1); }
    45% { transform: scale(1.1); }
}

.action {
    width: 100%;
    margin-top: 20px;
    padding: 15px 18px;
    border: 1px solid rgba(255, 255, 255, .2);
    border-radius: 30px;
    color: white;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: .5px;
    background: linear-gradient(100deg, #e91e83, #8e36ff);
    box-shadow: 0 0 25px rgba(222, 36, 161, .25);
    cursor: pointer;
    transition: transform .2s, box-shadow .2s;
    touch-action: manipulation;
}

.action:active {
    transform: scale(.97);
    box-shadow: 0 0 35px rgba(255, 36, 161, .5);
}

#heart {
    display: block;
    margin: 22px auto;
    padding: 5px;
    border: none;
    outline: none;
    background: transparent;
    font-size: 125px;
    cursor: pointer;
    filter: drop-shadow(0 0 15px #ff168d);
    animation: heartbeat 1.15s infinite;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}

#heart:active {
    transform: scale(1.2);
}

#status {
    min-height: 38px;
    margin-top: 15px;
    color: #ffb8e4;
    font-size: 13px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

.hidden {
    display: none !important;
}

#invite {
    display: none;
    overflow-wrap: anywhere;
    margin-top: 20px;
    color: #ffb8e4;
    font-size: 13px;
    line-height: 1.8;
}

#inviteLink {
    color: #ffb8e4;
    overflow-wrap: anywhere;
}

.footer {
    margin-top: 24px;
    font-size: 11px;
    color: #887592;
    letter-spacing: 1px;
}

.floating-heart {
    position: fixed;
    bottom: -30px;
    z-index: 1;
    pointer-events: none;
    animation: floatUp 5s linear forwards;
    filter: drop-shadow(0 0 7px #ff3fa9);
}

@keyframes floatUp {
    0% {
        opacity: 0;
        transform: translateY(0) rotate(0deg) scale(.7);
    }
    15% { opacity: .8; }
    85% { opacity: .7; }
    100% {
        opacity: 0;
        transform: translateY(-110vh) rotate(35deg) scale(1.2);
    }
}

</style>
</head>

<body>

<div id="universe">
    <div class="nebula one"></div>
    <div class="nebula two"></div>
</div>

<div class="screen">

    <!-- Invitation creation screen -->
    <div class="card" id="setup">
        <div class="eyebrow">Your Private Universe</div>

        <h1>Touch & Vibe</h1>

        <div class="small-heart">💗</div>

        <p class="subtitle">
            A little connection between two hearts,
            no matter how far apart they are.
        </p>

        <button class="action" id="create">
            Create Our Private Link 💌
        </button>

        <div id="invite">
            <p>Your invitation is ready ❤️</p>
            <a id="inviteLink" href="#"></a>
            <button class="action" id="copy">Copy Invitation Link</button>
        </div>

        <div class="footer">MADE WITH LOVE ✦</div>
    </div>

    <!-- Welcome screen -->
    <div class="card hidden" id="welcome">
        <div class="eyebrow">A little universe for two</div>

        <h1>abu ubaida <span style="color:#ff68b5">❤️</span> Sania</h1>

        <div class="small-heart">💖</div>

        <p class="subtitle">
            Miles may keep us apart,<br>
            but a little touch can bring us closer.
        </p>

        <p class="subtitle">
            Welcome to our little universe ✨
        </p>

        <button class="action" id="enter">
            Enter Our Universe 💌
        </button>

        <div class="footer">TWO HEARTS · ONE CONNECTION</div>
    </div>

    <!-- Heart screen -->
    <div class="card hidden" id="heartArea">
        <div class="eyebrow">Our Little Universe</div>

        <h1>Allen <span style="color:#ff68b5">❤️</span> Sania</h1>

        <p class="subtitle">
            Even when we're far apart,<br>
            send a little touch from the heart.
        </p>

        <button id="heart" aria-label="Send a heart">❤️</button>

        <p id="status">Connecting to your universe...</p>

        <p class="subtitle">
            Touch the heart to send a little love 💗
        </p>

        <div class="footer">ALWAYS CONNECTED IN HEART ✦</div>
    </div>

</div>

<script>
const setup = document.getElementById("setup");
const welcome = document.getElementById("welcome");
const heartArea = document.getElementById("heartArea");
const heart = document.getElementById("heart");
const statusText = document.getElementById("status");

const roomMatch = location.pathname.match(
    /^\/r\/([A-Za-z0-9_-]+)$/
);

let socket = null;
let retryTimer = null;
let currentRoom = null;
let manuallyClosed = false;

function createStars() {
    const universe = document.getElementById("universe");

    for (let i = 0; i < 100; i++) {
        const star = document.createElement("div");
        star.className = "star";
        star.style.left = Math.random() * 100 + "%";
        star.style.top = Math.random() * 100 + "%";
        star.style.animationDelay = Math.random() * 3 + "s";
        star.style.animationDuration =
            (1.5 + Math.random() * 3) + "s";

        universe.appendChild(star);
    }
}

function floatingHeart() {
    const item = document.createElement("div");
    item.className = "floating-heart";
    item.textContent = ["💗", "💕", "💖", "♡"][Math.floor(
        Math.random() * 4
    )];

    item.style.left = Math.random() * 95 + "%";
    item.style.fontSize = (14 + Math.random() * 20) + "px";
    item.style.animationDuration = (4 + Math.random() * 4) + "s";

    document.body.appendChild(item);

    setTimeout(() => item.remove(), 8500);
}

createStars();
setInterval(floatingHeart, 1100);

async function createInvitation() {
    const button = document.getElementById("create");

    button.disabled = true;
    button.textContent = "Creating your link...";

    try {
        const response = await fetch("/create-room", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Could not create link");
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
            } catch (error) {
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

function showWelcome() {
    setup.classList.add("hidden");
    heartArea.classList.add("hidden");
    welcome.classList.remove("hidden");
}

function showHeartScreen() {
    setup.classList.add("hidden");
    welcome.classList.add("hidden");
    heartArea.classList.remove("hidden");

    if (currentRoom) {
        connectRoom(currentRoom);
    }
}

document.getElementById("enter").addEventListener(
    "click", showHeartScreen
);

function animateHeart() {
    heart.animate(
        [
            { transform: "scale(1)" },
            { transform: "scale(1.4)" },
            { transform: "scale(1)" }
        ],
        {
            duration: 500,
            easing: "ease-out"
        }
    );

    floatingHeart();
    floatingHeart();
}

function vibratePhone() {
    if (typeof navigator.vibrate !== "function") {
        statusText.textContent =
            "Heart received ❤️ — vibration is not supported here.";
        return;
    }

    try {
        const result = navigator.vibrate([200, 100, 200]);

        if (result) {
            statusText.textContent =
                "A little love arrived! 💗";
        } else {
            statusText.textContent =
                "Heart received ❤️ — vibration may be blocked.";
        }
    } catch (error) {
        statusText.textContent =
            "Heart received ❤️ — vibration was blocked.";
    }
}

function connectRoom(roomId) {
    if (socket &&
        (socket.readyState === WebSocket.OPEN ||
         socket.readyState === WebSocket.CONNECTING)) {
        return;
    }

    manuallyClosed = false;

    const protocol =
        location.protocol === "https:" ? "wss:" : "ws:";

    socket = new WebSocket(
        protocol + "//" + location.host + "/ws/" + roomId
    );

    socket.onopen = () => {
        statusText.textContent = "Connected to our universe ❤️";
    };

    socket.onmessage = (event) => {
        if (event.data === "touch") {
            animateHeart();
            vibratePhone();
        }
    };

    socket.onerror = () => {
        statusText.textContent = "Connection issue. Reconnecting...";
    };

    socket.onclose = () => {
        if (!manuallyClosed && currentRoom) {
            statusText.textContent = "Reconnecting... 💗";

            clearTimeout(retryTimer);

            retryTimer = setTimeout(() => {
                socket = null;
                connectRoom(currentRoom);
            }, 3000);
        }
    };
}

if (roomMatch) {
    currentRoom = roomMatch[1];
    showWelcome();
}

heart.addEventListener("click", () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        if (typeof navigator.vibrate === "function") {
            navigator.vibrate(80);
        }

        socket.send("touch");
        animateHeart();

        statusText.textContent = "Your heart was sent! ❤️";
    } else {
        statusText.textContent =
            "Connecting... please try again in a moment.";
    }
});

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

    return JSONResponse({"path": f"/r/{room_id}"})


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
@app.get("/manifest.json")
async def manifest():
    return JSONResponse({
        "id": "/",
        "name": "Touch & Vibe - Abu Ubaida ❤️ Sania",
        "short_name": "Touch & Vibe",
        "description": "A special heart connection between Abu Ubaida and Sania.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#08030d",
        "theme_color": "#08030d",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any"
            },
            {
                "src": "/static/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any"
            }
        ]
    })
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
