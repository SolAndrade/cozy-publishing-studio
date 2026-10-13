from backend.domain.project import PublishingProject
from backend.storage.codec import project_from_json, project_to_json


class PostgresProjectStore:
    """Shared project persistence backed by PostgreSQL."""

    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError("database_url is required")
        self.database_url=database_url
        self._ensure_schema()

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("PostgreSQL storage requires the psycopg package") from exc
        return psycopg.connect(self.database_url)

    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cozy_projects (
                    id TEXT PRIMARY KEY,
                    payload JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)

    def save(self, project: PublishingProject):
        payload=project_to_json(project)
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO cozy_projects (id,payload,updated_at)
                   VALUES (%s,%s::jsonb,NOW())
                   ON CONFLICT (id) DO UPDATE
                   SET payload=EXCLUDED.payload, updated_at=NOW()""",
                (project.id,payload),
            )
        return project.id

    def load(self, project_id: str):
        with self._connect() as conn:
            row=conn.execute(
                "SELECT payload::text FROM cozy_projects WHERE id=%s",(project_id,)
            ).fetchone()
        if row is None:
            raise FileNotFoundError(project_id)
        return project_from_json(row[0])

    def list_ids(self):
        with self._connect() as conn:
            rows=conn.execute("SELECT id FROM cozy_projects ORDER BY updated_at DESC").fetchall()
        return [row[0] for row in rows]
