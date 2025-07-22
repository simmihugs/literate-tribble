from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    BackgroundTasks,
)

from fastapi.middleware.cors import CORSMiddleware
from inference_point import router as inference_router


app = FastAPI()

origins = ["http://localhost:5173", "http://192.168.178.22:5173", ""]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inference_router)


@app.get("/")
def root():
    return {"status": "ok"}
