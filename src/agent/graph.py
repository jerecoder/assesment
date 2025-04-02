import json
import logging
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.messages import FunctionMessage, HumanMessage, AIMessage
from src.agent.prompts import AGENT_PROMPT
from src.tools.sql_tools import execute_sql
from src.agent.state import AgentState
from typing import Optional

logging.basicConfig(level=logging.INFO)

def create_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [execute_sql]
    tool_functions = [convert_to_openai_function(t) for t in tools]

    MAX_QUERIES = 5
    MAX_RECURSION = 5

    def agent_func(state: AgentState) -> dict:
        try:
            if state.get("answer") is not None:
                return {"next": "end", "answer": state["answer"]}

            recursion_count = state.get("recursion_count", 0)
            if recursion_count >= MAX_RECURSION:
                logging.info(f"Límite de recursión alcanzado: {recursion_count}")
                return {
                    "next": "end",
                    "answer": "Demasiado difícil (>﹏<)"
                }

            query_count = state.get("query_count", 0)
            if query_count >= MAX_QUERIES:
                logging.info(f"Límite de consultas alcanzado: {query_count}")
                return {
                    "next": "end",
                    "answer": "Límite de consultas alcanzado. Por favor, refine su pregunta."
                }

            logging.info(f"Paso del agente: recursion_count={recursion_count}, query_count={query_count}")

            messages = state.get("messages", [])
            llm_messages = [HumanMessage(content=AGENT_PROMPT)]

            if messages:
                llm_messages.extend(messages)

            if state.get("action_input") is None and any(isinstance(msg, FunctionMessage) for msg in messages):
                final_message = HumanMessage(
                    content="Basándote en la información anterior, por favor, proporciona la respuesta final sin realizar nuevas consultas SQL."
                )
                if not messages or messages[-1].content != final_message.content:
                    llm_messages.append(final_message)

            response = llm.invoke(llm_messages, functions=tool_functions)

            if response.additional_kwargs.get("function_call"):
                return {
                    "next": "tool",
                    "action_input": {
                        "name": response.additional_kwargs["function_call"]["name"],
                        "arguments": response.additional_kwargs["function_call"]["arguments"]
                    },
                    "query_count": query_count + 1,
                    "recursion_count": recursion_count + 1
                }

            return {
                "next": "end",
                "answer": response.content
            }
        except Exception as e:
            logging.error(f"Error en agent_func: {e}")
            return {
                "next": "end",
                "answer": f"Error del agente: {str(e)}"
            }

    def tool_func(state: AgentState) -> dict:
        try:
            recursion_count = state.get("recursion_count", 0)
            if recursion_count >= MAX_RECURSION:
                logging.info(f"Límite de recursión alcanzado en tool_func: {recursion_count}")
                return {
                    "next": "end",
                    "answer": "Demasiado difícil (>﹏<)"
                }

            query_count = state.get("query_count", 0)
            logging.info(f"Paso de la herramienta: recursion_count={recursion_count}, query_count={query_count}")

            action_input = state.get("action_input")
            if not action_input or not isinstance(action_input, dict):
                return {
                    "next": "end",
                    "answer": "Entrada de herramienta inválida: No se proporcionó action_input"
                }

            tool_name = action_input.get("name")
            if not tool_name:
                return {
                    "next": "end",
                    "answer": "Entrada de herramienta inválida: No se especificó el nombre de la herramienta"
                }

            try:
                tool_args = json.loads(action_input.get("arguments", "{}"))
            except json.JSONDecodeError:
                return {
                    "next": "end",
                    "answer": "Argumentos de herramienta inválidos: No se pudo analizar JSON"
                }

            result = execute_sql.invoke(tool_args)

            updated_messages = state.get("messages", []) + [FunctionMessage(content=str(result), name=tool_name)]
            return {
                "next": "agent",
                "messages": updated_messages,
                "action_input": None,
                "recursion_count": recursion_count + 1,
                "query_count": query_count
            }
        except Exception as e:
            logging.error(f"Error en tool_func: {e}")
            return {
                "next": "end",
                "answer": f"Error de la herramienta: {str(e)}"
            }

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_func)
    workflow.add_node("tool", tool_func)

    workflow.add_conditional_edges(
        "agent",
        lambda state: "end" if state.get("action_input") is None and any(isinstance(msg, FunctionMessage) for msg in state.get("messages", [])) else "tool",
        {"end": "__end__", "tool": "tool"}
    )

    workflow.add_conditional_edges(
        "tool",
        lambda state: "agent" if state.get("action_input") is None else "end",
        {"agent": "agent", "end": "__end__"}
    )

    workflow.set_entry_point("agent")
    return workflow.compile()
