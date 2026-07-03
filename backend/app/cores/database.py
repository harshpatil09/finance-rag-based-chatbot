from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.cores.config import settings

# connect_args for MySQL: autocommit off, unicode handling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # test connection before using from pool (prevents stale conn errors)
    pool_recycle=3600,    # recycle connections every hour (MySQL drops idle connections)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()