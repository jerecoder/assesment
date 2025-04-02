from typing import TypedDict, List, Optional, Dict
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # For fields that accumulate values (like message history)
    messages: Annotated[List[BaseMessage], operator.add]
    
    # For fields that should keep the last value (single value updates)
    next: Annotated[str, "last"]
    action_input: Annotated[Optional[Dict], "last"]
    answer: Annotated[Optional[str], "last"]