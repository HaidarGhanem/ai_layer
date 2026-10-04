import psycopg

from services.tools.state import ToolIndexState
from services.tools.state_store import ToolStateStore


class PostgresToolStateStore(ToolStateStore):

    def __init__(
        self,
        dsn: str,
        table_name: str = "ai_tool_state",
    ):
        self.dsn = dsn
        self.table_name = table_name

        self._create_table()

    def _connect(self):

        return psycopg.connect(
            self.dsn
        )

    def _create_table(self):

        query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                tool_id TEXT PRIMARY KEY,
                fingerprint TEXT NOT NULL,
                indexed_fingerprint TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """

        with self._connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query
                )

    def get(
        self,
        tool_id: str,
    ) -> ToolIndexState | None:

        query = f"""
            SELECT
                tool_id,
                fingerprint,
                indexed_fingerprint,
                version
            FROM {self.table_name}
            WHERE tool_id = %s
        """

        with self._connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (tool_id,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return ToolIndexState(
            tool_id=row[0],
            fingerprint=row[1],
            indexed_fingerprint=row[2],
            version=row[3],
        )

    def save(
        self,
        state: ToolIndexState,
    ) -> None:

        query = f"""
            INSERT INTO {self.table_name} (
                tool_id,
                fingerprint,
                indexed_fingerprint,
                version,
                updated_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                NOW()
            )
            ON CONFLICT (tool_id)
            DO UPDATE SET
                fingerprint = EXCLUDED.fingerprint,
                indexed_fingerprint = EXCLUDED.indexed_fingerprint,
                version = EXCLUDED.version,
                updated_at = NOW()
        """

        with self._connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (
                        state.tool_id,
                        state.fingerprint,
                        state.indexed_fingerprint,
                        state.version,
                    ),
                )

    def delete(
        self,
        tool_id: str,
    ) -> None:

        query = f"""
            DELETE FROM {self.table_name}
            WHERE tool_id = %s
        """

        with self._connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (tool_id,),
                )

    def get_all(
        self,
    ) -> list[ToolIndexState]:

        query = f"""
            SELECT
                tool_id,
                fingerprint,
                indexed_fingerprint,
                version
            FROM {self.table_name}
            ORDER BY tool_id
        """

        with self._connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query
                )

                rows = cursor.fetchall()

        return [
            ToolIndexState(
                tool_id=row[0],
                fingerprint=row[1],
                indexed_fingerprint=row[2],
                version=row[3],
            )
            for row in rows
        ]