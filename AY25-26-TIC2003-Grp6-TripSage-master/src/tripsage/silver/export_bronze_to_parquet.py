from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tripsage.db.connection import DatabaseManager


class BronzeLayerExporter:
    def __init__(self, db_manager=None, schema_name="raw", output_dir="data/raw"):
        self.db_manager = db_manager or DatabaseManager()
        self.schema_name = schema_name
        self.output_dir = Path(output_dir)

    def get_table_names(self):
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """

        with self.db_manager.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (self.schema_name,))
                rows = cur.fetchall()

        return [row[0] for row in rows]

    def read_table(self, table_name):
        query = f'SELECT * FROM "{self.schema_name}"."{table_name}";'
        with self.db_manager.connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_output_path(self, table_name):
        return self.output_dir / f"{table_name}.parquet"

    def export_table(self, table_name):
        dataframe = self.read_table(table_name)
        output_path = self.get_output_path(table_name)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_parquet(output_path, index=False)
        print(f"Exported {self.schema_name}.{table_name} -> {output_path}")

    def run(self):
        table_names = self.get_table_names()
        if not table_names:
            print(f"No tables found in schema '{self.schema_name}'.")
            return

        for table_name in table_names:
            self.export_table(table_name)


def main():
    exporter = BronzeLayerExporter()
    exporter.run()


if __name__ == "__main__":
    main()