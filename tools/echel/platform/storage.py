from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProviderRecord:
    id: int
    name: str
    provider_type: str
    base_url: str
    model: str
    api_key: str


class PlatformStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    provider_type TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    model TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id INTEGER NOT NULL,
                    provider_id INTEGER,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (thread_id) REFERENCES threads(id),
                    FOREIGN KEY (provider_id) REFERENCES providers(id)
                );
                """
            )

    def upsert_provider(self, name: str, provider_type: str, base_url: str, model: str, api_key: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO providers(name, provider_type, base_url, model, api_key)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    provider_type=excluded.provider_type,
                    base_url=excluded.base_url,
                    model=excluded.model,
                    api_key=excluded.api_key
                """,
                (name, provider_type, base_url, model, api_key),
            )
            if cur.lastrowid:
                return int(cur.lastrowid)
            row = conn.execute("SELECT id FROM providers WHERE name = ?", (name,)).fetchone()
            return int(row["id"])

    def list_providers(self) -> list[ProviderRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, provider_type, base_url, model, api_key FROM providers ORDER BY id"
            ).fetchall()
        return [ProviderRecord(**dict(r)) for r in rows]

    def get_provider(self, provider_id: int) -> ProviderRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, provider_type, base_url, model, api_key FROM providers WHERE id = ?",
                (provider_id,),
            ).fetchone()
        return ProviderRecord(**dict(row)) if row else None

    def create_thread(self, title: str) -> int:
        with self._connect() as conn:
            cur = conn.execute("INSERT INTO threads(title) VALUES (?)", (title,))
            return int(cur.lastrowid)

    def list_threads(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id, title, created_at FROM threads ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def append_message(self, thread_id: int, role: str, content: str, provider_id: int | None = None) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO messages(thread_id, provider_id, role, content) VALUES (?, ?, ?, ?)",
                (thread_id, provider_id, role, content),
            )
            return int(cur.lastrowid)

    def list_messages(self, thread_id: int) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, thread_id, provider_id, role, content, created_at
                FROM messages
                WHERE thread_id = ?
                ORDER BY id ASC
                """,
                (thread_id,),
            ).fetchall()
        return [dict(r) for r in rows]
