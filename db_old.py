from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"  # 絶対パスで固定

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)

