"""SQLite Mock 数据：台区、表计、日采集成功率。"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "meter_mock.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化表结构并写入种子数据。"""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS districts (
                district_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                meter_count INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS meters (
                meter_id TEXT PRIMARY KEY,
                district_id TEXT NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS collect_daily (
                district_id TEXT NOT NULL,
                stat_date TEXT NOT NULL,
                success_rate REAL NOT NULL,
                fail_count INTEGER NOT NULL,
                PRIMARY KEY (district_id, stat_date)
            );
            """
        )
        conn.execute("DELETE FROM districts")
        conn.execute("DELETE FROM meters")
        conn.execute("DELETE FROM collect_daily")

        districts = [
            ("TQ-10001", "阳光花园台区", 80),
            ("TQ-10086", "工业园台区", 120),
        ]
        conn.executemany(
            "INSERT INTO districts (district_id, name, meter_count) VALUES (?, ?, ?)",
            districts,
        )

        meters = [
            ("M-10001-01", "TQ-10001", "normal"),
            ("M-10001-02", "TQ-10001", "normal"),
            ("M-10086-01", "TQ-10086", "normal"),
            ("M-10086-02", "TQ-10086", "stop_collect"),
            ("M-10086-03", "TQ-10086", "stop_collect"),
            ("M-10086-04", "TQ-10086", "clock_error"),
            ("M-10086-05", "TQ-10086", "stop_collect"),
        ]
        conn.executemany(
            "INSERT INTO meters (meter_id, district_id, status) VALUES (?, ?, ?)",
            meters,
        )

        daily = [
            ("TQ-10001", "2026-05-28", 0.98, 2),
            ("TQ-10086", "2026-05-28", 0.72, 34),
            ("TQ-10086", "2026-05-27", 0.75, 30),
        ]
        conn.executemany(
            "INSERT INTO collect_daily (district_id, stat_date, success_rate, fail_count) VALUES (?, ?, ?, ?)",
            daily,
        )
        conn.commit()
    finally:
        conn.close()


def fetch_district_snapshot(district_id: str) -> dict | None:
    """查询台区档案、最新采集指标、表计状态统计。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT district_id, name, meter_count FROM districts WHERE district_id = ?",
            (district_id,),
        ).fetchone()
        if not row:
            return None

        daily = conn.execute(
            """
            SELECT stat_date, success_rate, fail_count
            FROM collect_daily
            WHERE district_id = ?
            ORDER BY stat_date DESC
            LIMIT 1
            """,
            (district_id,),
        ).fetchone()

        status_rows = conn.execute(
            """
            SELECT status, COUNT(*) AS cnt
            FROM meters
            WHERE district_id = ?
            GROUP BY status
            """,
            (district_id,),
        ).fetchall()
        status_map = {r["status"]: r["cnt"] for r in status_rows}

        return {
            "district_id": row["district_id"],
            "name": row["name"],
            "meter_count": row["meter_count"],
            "latest": dict(daily) if daily else None,
            "stop_collect_count": status_map.get("stop_collect", 0),
            "clock_error_count": status_map.get("clock_error", 0),
        }
    finally:
        conn.close()
