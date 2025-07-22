import os
import asyncio

from dotenv import load_dotenv
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException

from huggingface_hub import get_inference_endpoint, InferenceEndpoint


from my_logging import my_logger

logger = my_logger()


assert load_dotenv(), "Failed to load environment variables from .env file"

router = APIRouter(
    prefix="/inference",
    tags=["inference"],
    responses={404: {"description": "inference not accessible"}},
)

endpoint: InferenceEndpoint = get_inference_endpoint(
    "telehealth-helper-wcc", token=os.getenv("HF_TOKEN")
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket: Connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket: Disconnected. Total: {len(self.active_connections)}"
            )

    async def broadcast(self, data: dict):
        """Send data to all clients. Remove disconnected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"WebSocket send error: {e}")
                disconnected.append(connection)
        for connection in disconnected:
            self.disconnect(connection)


manager_ws = ConnectionManager()


@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await manager_ws.connect(websocket)
    try:
        last_status = None
        while True:
            endpoint.fetch()
            current_status = endpoint.status
            if current_status != last_status:
                await manager_ws.broadcast({"status": current_status})
                last_status = current_status
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        manager_ws.disconnect(websocket)


@router.get("/resume")
async def resume_endpoint():
    try:
        endpoint.resume()  # .wait(timeout=360)
        return {"status": endpoint.status}
    except Exception as exp:
        logger.error(f"Error during resume: {exp}")
        raise HTTPException(504, "Endpoint resume timed out")


@router.get("/pause")
async def pause_endpoint():
    try:
        endpoint.pause()
        return {"status": endpoint.status}
    except Exception as exp:
        logger.error(f"Error during pause: {exp}")
        raise HTTPException(504, "Endpoint pause timed out")
