import sqlite3
import pandas as pd
import logging
from src.ui.console import console

logger = logging.getLogger(__name__)

def setup_database(db_name: str = "stops.db") -> sqlite3.Connection:
    with console.status("[bold green]Configurando base de datos SQLite...") as status:
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS stops")
            cursor.execute('''
                CREATE TABLE stops (
                    stop_id TEXT PRIMARY KEY,
                    stop_type_id TEXT,
                    stop_type_name TEXT,
                    start_at DATETIME,
                    ends_at DATETIME,
                    duration_minutes REAL
                )
            ''')
            conn.commit()
            return conn
        except Exception as e:
            logger.exception("Error al configurar la base de datos")
            raise

def load_data_to_db(conn: sqlite3.Connection, csv_file: str = "simulated_stops.csv") -> bool:
    with console.status("[bold green]Cargando datos en la base de datos...") as status:
        try:
            df = pd.read_csv(csv_file)
            df['start_at'] = pd.to_datetime(df['start_at'])
            df['ends_at'] = pd.to_datetime(df['ends_at'])
            df.to_sql('stops', conn, if_exists='append', index=False)
            console.print(f"[green]✓[/green] Cargados {len(df)} registros en la base de datos.")
            return True
        except Exception as e:
            logger.exception("Error al cargar datos a la base de datos")
            return False 