from sqlmodel import create_engine, SQLModel

SQLITE_FILE_NAME = "scheduler.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=True, connect_args={"timeout": 15})

def create_database():
    SQLModel.metadata.create_all(engine)
