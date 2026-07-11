"""数据库引擎 — SQLite WAL 模式连接管理与表创建。"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional

from autosoc.core.config import settings


class Database:
    """线程安全的 SQLite 数据库封装，默认 WAL 模式提升并发读性能。"""

    _instance: Optional["Database"] = None
    _lock = threading.Lock()

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._local = threading.local()

    @classmethod
    def get_instance(cls) -> "Database":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(settings.db_path)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """获取当前线程的数据库连接（每个线程独立连接）。"""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute("PRAGMA busy_timeout=5000;")
            self._local.conn = conn
        return self._local.conn

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self.get_connection()
        return conn.execute(sql, params)

    def executemany(self, sql: str, params_list: list[tuple]) -> sqlite3.Cursor:
        conn = self.get_connection()
        return conn.executemany(sql, params_list)

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        return self.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self.execute(sql, params).fetchall()

    def insert(self, sql: str, params: tuple = ()) -> int:
        conn = self.get_connection()
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

    def commit(self):
        self.get_connection().commit()

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

    def initialize_schema(self, schema_path: str = "data/schema.sql"):
        """从 SQL 文件初始化数据库表结构。"""
        path = Path(schema_path)
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        sql = path.read_text(encoding="utf-8")
        conn = self.get_connection()
        conn.executescript(sql)
        conn.commit()
