from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    BackgroundTasks,
)

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

from database import SessionLocal, init_db, PDF
from models import PDFCreate, PDFResponse

# Initialize DB
init_db()

# FastAPI app
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://192.168.178.31:5173",
    "http://localhost:3000",
    "http://192.168.178.22:5173",
    # add any other frontend URLs you'll use in dev or prod
]

# CORS (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- For WebSocket broadcast ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


def broadcast_pdfs_sync(db):
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(broadcast_pdfs(db))
    loop.close()


# --- REST endpoint: Create PDF ---
@app.post("/create", response_model=PDFResponse)
def create_pdf(
    pdf: PDFCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    db_pdf = PDF(name=pdf.name)
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    # Schedule the broadcast to run after the response is returned
    background_tasks.add_task(broadcast_pdfs_sync, db)
    return db_pdf


# --- Helper to broadcast PDFs list ---
async def broadcast_pdfs(db):
    pdfs = db.query(PDF).all()
    pdf_list = [
        {"id": pdf.id, "name": pdf.name, "date": str(pdf.date), "creator": pdf.creator}
        for pdf in pdfs
    ]
    await manager.broadcast(json.dumps({"pdfs": pdf_list}))


# --- WebSocket for live updates ---
@app.websocket("/ws/pdfs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    db = next(get_db())

    try:
        # On connect, send current PDFs
        await broadcast_pdfs(db)
        while True:
            # Client messages not used, but can be handled here
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
