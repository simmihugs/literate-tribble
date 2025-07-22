import asyncio
import websockets
import json

WS_URL = "ws://192.168.178.22:8000/inference/ws/status"


async def listen_status():
    last_status = None
    async with websockets.connect(WS_URL) as websocket:
        print(f"Connected to {WS_URL} ...")
        while True:
            try:
                data = await websocket.recv()
                msg = json.loads(data)
                status = msg.get("status")
                if status != last_status:
                    print(f"Status: {status}")
                    last_status = status
            except websockets.ConnectionClosed:
                print("Connection closed")
                break


if __name__ == "__main__":
    asyncio.run(listen_status())
