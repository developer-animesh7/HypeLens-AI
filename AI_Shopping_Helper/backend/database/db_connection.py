"""Unified database connection (PostgreSQL via SQLAlchemy, SQLite fallback)."""

import os
import logging
from typing import Any, Dict, Iterable, List, Optional, Mapping, Sequence

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Result
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Load .env so DATABASE_URL and other vars are available in scripts and app
load_dotenv()


def _default_sqlite_url() -> str:
    # Preserve old default path if DATABASE_URL is not provided
    os.makedirs(os.path.dirname("data/shopping_assistant.db"), exist_ok=True)
    return f"sqlite:///data/shopping_assistant.db"


class DatabaseConnection:
    """Connection wrapper exposing simple query/execute helpers."""

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("DATABASE_URL") or _default_sqlite_url()
        # For SQLite: check_same_thread must be False sometimes; SQLAlchemy handles this via connect_args
        connect_args = {"check_same_thread": False} if self.url.startswith("sqlite") else {}
        self.engine: Engine = create_engine(self.url, future=True, pool_pre_ping=True, connect_args=connect_args)

    def connect(self):
        # Kept for backward compatibility; engine manages pools
        logger.info(f"Database engine ready: {self.url}")

    def disconnect(self):
        try:
            self.engine.dispose()
            logger.info("Database engine disposed")
        except Exception:
            pass

    def execute_query(self, query: str, params: Optional[Mapping[str, Any] | Sequence[Any]] = None) -> List[Dict[str, Any]]:
        try:
            with self.engine.connect() as conn:
                if params is None:
                    result: Result = conn.execute(text(query))
                else:
                    result: Result = conn.execute(text(query), params)
                rows = result.mappings().all()  # returns list of RowMapping (dict-like)
                return [dict(r) for r in rows]
        except SQLAlchemyError as e:
            logger.error(f"Error executing query: {e}")
            raise

    def execute_update(self, query: str, params: Optional[Mapping[str, Any] | Sequence[Any]] = None) -> int:
        try:
            with self.engine.begin() as conn:
                if params is None:
                    result: Result = conn.execute(text(query))
                else:
                    result: Result = conn.execute(text(query), params)
                try:
                    rc = result.rowcount  # type: ignore[attr-defined]
                except Exception:
                    rc = 0
                return int(rc or 0)
        except SQLAlchemyError as e:
            logger.error(f"Error executing update: {e}")
            raise

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        try:
            with self.engine.begin() as conn:
                total = 0
                # Use executemany-style by passing list of dicts directly
                result: Result = conn.execute(text(query), params_list)  # type: ignore[arg-type]
                try:
                    total = int(result.rowcount or 0)  # type: ignore[attr-defined]
                except Exception:
                    # Fallback approximate count
                    total = len(params_list)
                return total
        except SQLAlchemyError as e:
            logger.error(f"Error executing batch update: {e}")
            raise

    def get_last_insert_id(self) -> Optional[int]:
        # SQLAlchemy usually returns this via RETURNING; this helper left as a no-op
        return None


def init_db():
    """No-op initializer in clean mode. Provide migrations separately."""
    logger.info("init_db skipped (clean mode). Use migrations to manage schema.")
