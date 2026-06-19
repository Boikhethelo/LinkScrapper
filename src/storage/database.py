import csv
import json
import os
import sqlite3
from pathlib import Path

from src.models.profile import LinkedInProfile
from src.utils.logger import logger
from config.settings import settings

class ProfileDatabase:

    """
    Stores scraped LinkedIn profiles in a local SQLite database
    and provides CSV export.

    JSON columns (experience, education, skills) store serialised
    lists so the full structured data is preserved.

    Usage:
        db = ProfileDatabase()
        db.save(profile)
        db.export_csv("data/output/results.csv")
        db.close()
    """

    def __init__(self, db_path: str = None):
        path = Path(db_path or settings.DB_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row         # Dict-like access
        self._create_table()
        logger.info(f"Database ready at {path}")

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url  TEXT UNIQUE NOT NULL,
                full_name    TEXT,
                headline     TEXT,
                location     TEXT,
                about        TEXT,
                connections  TEXT,
                followers    INTEGER,
                experience   TEXT,   -- JSON array
                education    TEXT,   -- JSON array
                skills       TEXT,   -- JSON array
                source       TEXT,
                scraped_at   TEXT
            )
        """)
        self.conn.commit()
    # ==============================================================
    #                             Write
    # ==============================================================

    def save(self, profile: LinkedInProfile):
        """Insert a profile, or update it if the URL already exists."""
        try:
            self.conn.execute(
                """
                INSERT INTO profiles
                    (profile_url, full_name, headline, location, about,
                     connections, followers, experience, education, skills,
                     source, scraped_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(profile_url) DO UPDATE SET
                    full_name   = excluded.full_name,
                    headline    = excluded.headline,
                    location    = excluded.location,
                    about       = excluded.about,
                    connections = excluded.connections,
                    followers   = excluded.followers,
                    experience  = excluded.experience,
                    education   = excluded.education,
                    skills      = excluded.skills,
                    source      = excluded.source,
                    scraped_at  = excluded.scraped_at
                """,
                (
                    profile.profile_url,
                    profile.full_name,
                    profile.headline,
                    profile.location,
                    profile.about,
                    profile.connections,
                    profile.followers,
                    json.dumps([e.model_dump() for e in profile.experience]),
                    json.dumps([e.model_dump() for e in profile.education]),
                    json.dumps([s.model_dump() for s in profile.skills]),
                    profile.source,
                    profile.scraped_at,
                ),
            )
            self.conn.commit()
            logger.info(f"💾 Saved: {profile.full_name}")

        except Exception as exc:
            logger.error(f"❌ DB save failed for {profile.profile_url}: {exc}")


    # ==========================================================================
    #                               Read
    # ==========================================================================

    def get_all(self) -> list[dict]:
        """Return all stored profiles as a list of dicts."""
        cursor = self.conn.execute("SELECT * FROM profiles ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]

    def already_scraped(self, url: str) -> bool:
        """Check if a URL has already been scraped (avoids duplicates)."""
        row = self.conn.execute(
            "SELECT 1 FROM profiles WHERE profile_url = ?", (url,)
        ).fetchone()
        return row is not None


    # ==========================================================================
    #                              Export
    # ==========================================================================

    def export_csv(self, output_path: str = None) -> str:
        """Export all profiles to a flat CSV file."""
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        path = output_path or os.path.join(settings.OUTPUT_DIR, "profiles.csv")
        rows = self.get_all()

        if not rows:
            logger.warning("No profiles to export.")
            return path

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"📄 Exported {len(rows)} profile(s) → {path}")
        return path

    def close(self):
        self.conn.close()