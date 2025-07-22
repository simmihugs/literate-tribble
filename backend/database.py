from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    creator = Column(String, default="Unknown")


def init_db():
    Base.metadata.create_all(bind=engine)
