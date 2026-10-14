from backend.domain.project import PublishingProject
from backend.storage.codec import project_from_json, project_to_json


class PostgresProjectStore:
    """Shared project persistence backed by PostgreSQL with optimistic writes."""

    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError("database_url is required")
        self.database_url = database_url
        self._loaded_revisions: dict[int, int] = {}
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
                    revision BIGINT NOT NULL DEFAULT 1,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            conn.execute(
                "ALTER TABLE cozy_projects ADD COLUMN IF NOT EXISTS revision BIGINT NOT NULL DEFAULT 1"
            )

    def save(self, project: PublishingProject):
        payload = project_to_json(project)
        object_key = id(project)
        expected_revision = self._loaded_revisions.get(object_key)
        with self._connect() as conn:
            if expected_revision is None:
                row = conn.execute(
                    """INSERT INTO cozy_projects (id,payload,revision,updated_at)
                       VALUES (%s,%s::jsonb,1,NOW())
                       ON CONFLICT (id) DO NOTHING
                       RETURNING revision""",
                    (project.id, payload),
                ).fetchone()
                if row is None:
                    raise RuntimeError("project_write_conflict")
                revision = row[0]
            else:
                row = conn.execute(
                    """UPDATE cozy_projects
                       SET payload=%s::jsonb, revision=revision+1, updated_at=NOW()
                       WHERE id=%s AND revision=%s
                       RETURNING revision""",
                    (payload, project.id, expected_revision),
                ).fetchone()
                if row is None:
                    raise RuntimeError("project_write_conflict")
                revision = row[0]
        self._loaded_revisions[object_key] = revision
        return project.id

    def load(self, project_id: str):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload::text,revision FROM cozy_projects WHERE id=%s",
                (project_id,),
            ).fetchone()
        if row is None:
            raise FileNotFoundError(project_id)
        project = project_from_json(row[0])
        self._loaded_revisions[id(project)] = row[1]
        return project

    def list_ids(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id FROM cozy_projects ORDER BY updated_at DESC"
            ).fetchall()
        return [row[0] for row in rows]
