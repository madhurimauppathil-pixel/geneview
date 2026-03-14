from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://postgres:admin123@localhost/dna_viewer"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Sequence(Base):
    __tablename__ = "sequences"
    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, index=True)
    organism  = Column(String, nullable=True)
    sequence  = Column(Text)
    uploaded  = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()