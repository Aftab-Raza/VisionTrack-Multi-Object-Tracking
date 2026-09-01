import sqlite3

from datetime import datetime, timezone
from pathlib import Path

import config


class DatabaseManager:

    def __init__(self):

        self.enabled = config.ENABLE_DATABASE

        self.connection = None

        if not self.enabled:
            return

        database_path = Path(
            config.DATABASE_PATH
        )

        database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            str(database_path)
        )

        self.connection.row_factory = (
            sqlite3.Row
        )

        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        # Better performance for applications
        # that perform frequent writes.
        self.connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        self.connection.execute(
            "PRAGMA synchronous = NORMAL"
        )

        self._create_tables()


    # ==========================================
    # Database Schema
    # ==========================================

    def _create_tables(self):

        if not self.enabled:
            return

        cursor = self.connection.cursor()


        # --------------------------------------
        # Sessions
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                started_at TEXT NOT NULL,

                ended_at TEXT,

                source TEXT NOT NULL,

                source_fps REAL,

                frame_width INTEGER,

                frame_height INTEGER,

                total_frames INTEGER DEFAULT 0,

                total_in INTEGER DEFAULT 0,

                total_out INTEGER DEFAULT 0,

                status TEXT DEFAULT 'running'

            )
            """
        )


        # --------------------------------------
        # Tracks
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tracks (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                session_id INTEGER NOT NULL,

                track_id INTEGER NOT NULL,

                class_name TEXT,

                first_frame INTEGER,

                last_frame INTEGER,

                first_seen_seconds REAL,

                last_seen_seconds REAL,

                last_centroid_x INTEGER,

                last_centroid_y INTEGER,

                max_confidence REAL,

                frames_seen INTEGER DEFAULT 1,

                UNIQUE(session_id, track_id),

                FOREIGN KEY(session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE

            )
            """
        )


        # --------------------------------------
        # Events
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                session_id INTEGER NOT NULL,

                event_type TEXT NOT NULL,

                track_id INTEGER,

                class_name TEXT,

                frame_index INTEGER,

                timestamp_seconds REAL,

                zone TEXT,

                direction TEXT,

                dwell_time REAL,

                centroid_x INTEGER,

                centroid_y INTEGER,

                snapshot_path TEXT,

                created_at TEXT NOT NULL,

                FOREIGN KEY(session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE

            )
            """
        )


        # --------------------------------------
        # Indexes
        # --------------------------------------

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_tracks_session
            ON tracks(session_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_events_session
            ON events(session_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_events_track
            ON events(track_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_events_type
            ON events(event_type)
            """
        )


        self.connection.commit()


    # ==========================================
    # Session Management
    # ==========================================

    def start_session(
        self,
        source,
        source_fps,
        frame_width,
        frame_height
    ):

        if not self.enabled:
            return None

        started_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )


        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO sessions
            (
                started_at,
                source,
                source_fps,
                frame_width,
                frame_height,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                started_at,
                str(source),
                source_fps,
                frame_width,
                frame_height,
                "running"
            )
        )


        self.connection.commit()

        return cursor.lastrowid


    def end_session(
        self,
        session_id,
        total_frames,
        total_in,
        total_out
    ):

        if (
            not self.enabled
            or
            session_id is None
        ):
            return


        ended_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )


        self.connection.execute(
            """
            UPDATE sessions

            SET
                ended_at = ?,
                total_frames = ?,
                total_in = ?,
                total_out = ?,
                status = 'completed'

            WHERE id = ?
            """,
            (
                ended_at,
                total_frames,
                total_in,
                total_out,
                session_id
            )
        )


        self.connection.commit()


    # ==========================================
    # Track Storage
    # ==========================================

    def upsert_track(
        self,
        session_id,
        obj,
        frame_index,
        timestamp
    ):

        if (
            not self.enabled
            or
            session_id is None
        ):
            return


        track_id = obj[
            "track_id"
        ]

        class_name = obj[
            "class_name"
        ]

        confidence = float(
            obj[
                "confidence"
            ]
        )

        cx, cy = obj[
            "centroid"
        ]


        # First create the track if it doesn't
        # already exist.

        self.connection.execute(
            """
            INSERT OR IGNORE INTO tracks
            (
                session_id,
                track_id,
                class_name,
                first_frame,
                last_frame,
                first_seen_seconds,
                last_seen_seconds,
                last_centroid_x,
                last_centroid_y,
                max_confidence,
                frames_seen
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                session_id,
                track_id,
                class_name,
                frame_index,
                frame_index,
                timestamp,
                timestamp,
                cx,
                cy,
                confidence
            )
        )


        # Now update the latest state.

        self.connection.execute(
            """
            UPDATE tracks

            SET
                class_name = ?,
                last_frame = ?,
                last_seen_seconds = ?,
                last_centroid_x = ?,
                last_centroid_y = ?,

                max_confidence =
                    MAX(
                        max_confidence,
                        ?
                    ),

                frames_seen =
                    frames_seen + 1

            WHERE
                session_id = ?
                AND
                track_id = ?
            """,
            (
                class_name,
                frame_index,
                timestamp,
                cx,
                cy,
                confidence,
                session_id,
                track_id
            )
        )


    # ==========================================
    # Event Storage
    # ==========================================

    def log_event(
        self,
        session_id,
        event,
        snapshot_path=None
    ):

        if (
            not self.enabled
            or
            session_id is None
        ):
            return


        created_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )


        self.connection.execute(
            """
            INSERT INTO events
            (
                session_id,
                event_type,
                track_id,
                class_name,
                frame_index,
                timestamp_seconds,
                zone,
                direction,
                dwell_time,
                centroid_x,
                centroid_y,
                snapshot_path,
                created_at
            )

            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?
            )
            """,
            (
                session_id,

                event.get(
                    "event_type"
                ),

                event.get(
                    "track_id"
                ),

                event.get(
                    "class_name"
                ),

                event.get(
                    "frame_index"
                ),

                event.get(
                    "timestamp_seconds"
                ),

                event.get(
                    "zone"
                ),

                event.get(
                    "direction"
                ),

                event.get(
                    "dwell_time"
                ),

                event.get(
                    "centroid_x"
                ),

                event.get(
                    "centroid_y"
                ),

                snapshot_path,

                created_at
            )
        )


    # ==========================================
    # Transaction Control
    # ==========================================

    def commit(self):

        if (
            self.enabled
            and
            self.connection is not None
        ):

            self.connection.commit()


    def close(self):

        if self.connection is not None:

            self.connection.commit()

            self.connection.close()

            self.connection = None


    # ==========================================
    # Query Helpers
    # ==========================================

    def get_recent_sessions(
        self,
        limit=10
    ):

        if not self.enabled:
            return []


        cursor = self.connection.execute(
            """
            SELECT *
            FROM sessions

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                limit,
            )
        )


        return [
            dict(row)
            for row in cursor.fetchall()
        ]


    def get_recent_events(
        self,
        limit=20
    ):

        if not self.enabled:
            return []


        cursor = self.connection.execute(
            """
            SELECT *
            FROM events

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                limit,
            )
        )


        return [
            dict(row)
            for row in cursor.fetchall()
        ]