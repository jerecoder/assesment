import os
import logging
import traceback
from dotenv import load_dotenv

from src.agent.agent import create_agent
from src.database.setup import setup_database, load_data_to_db
from src.ui.console import console, Prompt
from src.ui.texts import TEXTOS


load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    try:
        conn = setup_database(db_name="stops.db")
        load_data_to_db(conn, csv_file="simulated_stops.csv")

        agent = create_agent()

        thread_config = {"configurable": {"thread_id": "default_thread"}}

        console.print(TEXTOS["bienvenida"])

        while True:
            question = Prompt.ask(TEXTOS["prompt_pregunta"])

            if question.lower() == 'exit':
                console.print(TEXTOS["despedida"])
                break

            try:
                initial_state = {"messages": [{"role": "user", "content": question}]}

                result = agent.invoke(
                    initial_state, 
                    config=thread_config
                )

                console.print("\n[bold green]StopQuery:[/bold green]")
                
                last_message = result['messages'][-1]
                console.print(last_message.content)

            except Exception as e:
                logger.error("Error during execution:")
                logger.error(traceback.format_exc())
                console.print(f"{TEXTOS['error']} {str(e)}\n")
                console.print("[red]Error Traceback:[/red]")
                console.print(traceback.format_exc())

    except Exception as e:
        logger.error("Fatal error during execution:")
        logger.error(traceback.format_exc())
        console.print(f"{TEXTOS['error_fatal']} {str(e)}\n")
        console.print("[red]Error Traceback:[/red]")
        console.print(traceback.format_exc())
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()