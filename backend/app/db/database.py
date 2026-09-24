from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

db_url = settings.DATABASE_URL
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db_schema():
    """Auto-creates tables and dynamically migrates missing columns for SQLite."""
    Base.metadata.create_all(bind=engine)
    if db_url.startswith("sqlite"):
        try:
            inspector = inspect(engine)
            with engine.begin() as conn:
                if inspector.has_table("users"):
                    u_cols = [c["name"] for c in inspector.get_columns("users")]
                    if "age_difference" not in u_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN age_difference FLOAT"))
                    if "age_confidence" not in u_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN age_confidence FLOAT DEFAULT 0.95"))
                    if "chronological_age" not in u_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN chronological_age INTEGER"))
                    if "estimated_age" not in u_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN estimated_age FLOAT"))

                if inspector.has_table("moderation_results"):
                    m_cols = [c["name"] for c in inspector.get_columns("moderation_results")]
                    if "confidence" not in m_cols:
                        conn.execute(text("ALTER TABLE moderation_results ADD COLUMN confidence FLOAT DEFAULT 0.85"))
                    if "is_human_reviewed" not in m_cols:
                        conn.execute(text("ALTER TABLE moderation_results ADD COLUMN is_human_reviewed BOOLEAN DEFAULT 0"))
                    if "moderator_id" not in m_cols:
                        conn.execute(text("ALTER TABLE moderation_results ADD COLUMN moderator_id INTEGER"))
                    if "moderator_notes" not in m_cols:
                        conn.execute(text("ALTER TABLE moderation_results ADD COLUMN moderator_notes TEXT"))
                    if "processing_time_seconds" not in m_cols:
                        conn.execute(text("ALTER TABLE moderation_results ADD COLUMN processing_time_seconds FLOAT"))
        except Exception as e:
            pass

# Initialize schema on module import
init_db_schema()

def get_db():
    """Dependency for obtaining a database session per API request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
