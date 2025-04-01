from dotenv import load_dotenv
import pandas as pd
import sqlite3
import logging
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.syntax import Syntax
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Optional, Tuple, Dict, Any
import re
import json
import hashlib
from pathlib import Path

TEXTOS = {
    "bienvenida": """
[bold blue]¡Bienvenido a StopQuery![/bold blue]

Este sistema te permite hacer preguntas en lenguaje natural sobre las paradas
de máquina y las convierte en consultas SQL para su análisis.

[bold green]Ejemplos de Preguntas:[/bold green]
• ¿Cuántas paradas ocurrieron el 1 de enero?
• Lista todas las paradas causadas por 'Die Head Cleaning'
• ¿Cuál es la duración promedio de cada tipo de parada?
• ¿Qué hora del día tuvo la duración total de paradas más larga?

[bold yellow]Escribe 'exit' para salir[/bold yellow]
""",
    "prompt_pregunta": "\n[bold blue]Tu pregunta[/bold blue]",
    "despedida": "\n[bold yellow]¡Hasta luego![/bold yellow]",
    "generando_sql": "[bold green]Generando consulta SQL...[/bold green]",
    "ejecutando_query": "[bold green]Ejecutando consulta...[/bold green]",
    "consulta_generada": "\n[bold cyan]Consulta SQL Generada:[/bold cyan]",
    "resultados": "\n[bold green]Resultados:[/bold green]",
    "error": "\n[bold red]Error:[/bold red]",
    "error_fatal": "\n[bold red]Error Fatal:[/bold red]",
    "sin_resultados": "No se encontraron resultados.",
    "error_query": "Error al ejecutar la consulta: {}",
    "cache_hit": "[blue]Usando consulta en caché[/blue]",
    "cache_miss": "[yellow]Generando nueva consulta SQL...[/yellow]"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()
load_dotenv()

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "query_cache.json"

def setup_cache():
    CACHE_DIR.mkdir(exist_ok=True)
    if not CACHE_FILE.exists():
        CACHE_FILE.write_text("{}")

def get_cache_key(question: str) -> str:
    return hashlib.md5(question.lower().encode()).hexdigest()

def get_cached_query(question: str) -> Optional[str]:
    try:
        cache = json.loads(CACHE_FILE.read_text())
        cache_key = get_cache_key(question)
        if cache_key in cache:
            console.print(TEXTOS["cache_hit"])
            return cache[cache_key]
    except Exception as e:
        console.print(f"[red]Error al leer la caché: {str(e)}[/red]")
    return None

def cache_query(question: str, query: str):
    try:
        cache = json.loads(CACHE_FILE.read_text())
        cache_key = get_cache_key(question)
        cache[cache_key] = query
        CACHE_FILE.write_text(json.dumps(cache, indent=2))
    except Exception as e:
        console.print(f"[red]Error al escribir en la caché: {str(e)}[/red]")

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
        except FileNotFoundError:
            console.print(f"[red]Error:[/red] No se encontró el archivo {csv_file}.")
            return False
        except pd.errors.ParserError as e:
            console.print(f"[red]Error al analizar el CSV:[/red] {e}")
            return False
        try:
            df['start_at'] = pd.to_datetime(df['start_at'])
            df['ends_at'] = pd.to_datetime(df['ends_at'])
            df.to_sql('stops', conn, if_exists='append', index=False)
            console.print(f"[green]✓[/green] Cargados {len(df)} registros en la base de datos.")
            return True
        except Exception as e:
            logger.exception("Error al cargar datos a la base de datos")
            console.print(f"[red]Error:[/red] {e}")
            return False

def create_sql_generator():
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto en SQL. Convierte la siguiente pregunta sobre paradas de máquina en una consulta SQL. La base de datos tiene una tabla llamada 'stops' con columnas: stop_id (TEXT), stop_type_id (TEXT), stop_type_name (TEXT), start_at (DATETIME), ends_at (DATETIME), duration_minutes (REAL). Solo devuelve la consulta SQL, nada más. La consulta debe ser compatible con SQLite."),
            ("human", "{question}")
        ])
        return llm, prompt
    except Exception as e:
        logger.exception("Error al crear el generador de SQL")
        raise

def clean_sql_response(response: str) -> str:
    match = re.search(r"(?i)(SELECT .*?)(;|$)", response, re.DOTALL)
    return match.group(1).strip() if match else ""

def execute_query(conn: sqlite3.Connection, query: Optional[str]) -> Tuple[Optional[Table], Optional[str]]:
    try:
        if not query or not isinstance(query, str) or "stops" not in query.lower():
            return None, "La consulta SQL generada no es válida."
        logger.info(f"Ejecutando SQL: {query}")
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return None, "No se encontraron resultados."
        columns = [desc[0] for desc in cursor.description]
        table = Table(show_header=True, header_style="bold magenta")
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        return table, None
    except sqlite3.Error as e:
        return None, TEXTOS["error_query"].format(str(e))
    except Exception as e:
        logger.exception("Error durante la ejecución de la consulta")
        return None, f"Error inesperado: {str(e)}"

def display_welcome():
    console.print(Panel(TEXTOS["bienvenida"], title="[bold]Sistema de Análisis de Paradas de Máquina[/bold]", border_style="blue"))

def display_query_result(sql_query: str, results: Optional[Table], error: Optional[str] = None):
    console.print(TEXTOS["consulta_generada"])
    console.print(Syntax(sql_query, "sql", theme="monokai"))
    if error:
        console.print(f"{TEXTOS['error']} {error}")
        return
    if results:
        console.print(TEXTOS["resultados"])
        console.print(results)

def generate_sql_query(question: str) -> str:
    cached_query = get_cached_query(question)
    if cached_query:
        return cached_query

    console.print(TEXTOS["cache_miss"])
    
    try:
        llm, prompt = create_sql_generator()
        messages = prompt.format_messages(question=question)
        response = llm.invoke(messages)
        query = clean_sql_response(response.content)
        
        cache_query(question, query)
        
        return query
    except Exception as e:
        console.print(f"{TEXTOS['error']} {str(e)}")
        raise
