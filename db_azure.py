from sqlmodel import SQLModel, create_engine, Session
import csv
from sqlmodel import Session, select
from models import Space, PlanType, SpacePlan
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 環境変数の読み込み
base_path = Path(__file__).parent
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# データベース接続情報（Azure MySQL用）
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME')
SSL_CA_PATH = os.getenv('SSL_CA_PATH', 'DigiCertGlobalRootCA.crt.pem')

# MySQLのURL構築
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("DB_HOST =", DB_HOST)

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {
            "ca": SSL_CA_PATH
        }
    },
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
    
# デバッグ用：PlanTypeテーブルの内容を表示
if __name__ == "__main__":
    with Session(engine) as session:
        plan_types = session.exec(select(PlanType)).all()
        print("PlanType一覧:")
        for pt in plan_types:
            print(f"{pt.plan_type_id}: {pt.code} - {pt.name_ja} ({pt.unit_days}日)")