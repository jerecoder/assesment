import logging
import traceback
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.agent.graph import create_agent
from src.database.setup import setup_database, load_data_to_db
from src.ui.console import console, Prompt
from src.ui.texts import TEXTOS
from src.database.cache import setup_cache

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        setup_cache()
        conn = setup_database(db_name="stops.db")
        load_data_to_db(conn, csv_file="simulated_stops.csv")
        agent = create_agent()
        
        console.print(TEXTOS["bienvenida"])
        
        while True:
            question = Prompt.ask(TEXTOS["prompt_pregunta"])
            
            if question.lower() == 'exit':
                console.print(TEXTOS["despedida"])
                break
                
            try:
                initial_state = {
                    "messages": [HumanMessage(content=question)],
                    "next": "agent",
                    "action_input": None,
                    "answer": None
                }
                
                result = agent.invoke(initial_state)
                
                console.print("\n[bold green]Análisis:[/bold green]")
                console.print(result["answer"])
                
            except Exception as e:
                logger.error("Error durante la ejecución:")
                logger.error(traceback.format_exc()) 
                console.print(f"{TEXTOS['error']} {str(e)}\n")
                console.print("[red]Traza del error:[/red]")
                console.print(traceback.format_exc())
    
    except Exception as e:
        logger.error("Error fatal durante la ejecución:")
        logger.error(traceback.format_exc())
        console.print(f"{TEXTOS['error_fatal']} {str(e)}\n")
        console.print("[red]Traza del error:[/red]")
        console.print(traceback.format_exc())
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
