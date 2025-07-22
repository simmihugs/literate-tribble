from pydantic import BaseModel
import datetime


class PDFCreate(BaseModel):
    name: str


class PDFResponse(BaseModel):
    id: int
    name: str
    date: datetime.datetime
    creator: str

    class Config:
        orm_mode = True
