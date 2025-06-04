from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.memory.v2 import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.models.base import Model
from agno.storage.sqlite import SqliteStorage
from agno.tools.file import FileTools
from agno.tools.giphy import GiphyTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.python import PythonTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.shell import ShellTools
from .prompt import AGENT_DEV_DESCRIPTION, AGENT_DEV_INSTRUCTION
from .tools.pexels import PexelsTools


def load_local_storage():
    return SqliteStorage(
        table_name="agent_dev_sessions",
        db_file="../data.db"
    )

def load_agent_memory():
    return Memory(
        db=SqliteMemoryDb(table_name="memory", db_file="../data.db")
    )

# docker_tools = DockerTools(
#         enable_container_management=True,
#         enable_image_management=True,
#         enable_volume_management=True,
#         enable_network_management=True,
#     )

def build_agent(
        model: Model,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = True,
) -> Agent:
    additional_context = ""
    if user_id:
        additional_context += "<context>"
        additional_context += f"You are interacting with the user: {user_id}"
        additional_context += "</context>"

    return Agent(
        name="Dev Pet",
        agent_id="dev_pet",
        user_id=user_id,
        session_id=session_id,
        model=model,
        memory=load_agent_memory(),
        enable_agentic_memory=True,
        tools=[GoogleSearchTools(),
               ShellTools(),
               PythonTools(),
               FileTools(),
               GiphyTools(),
               PexelsTools(),
               # DockerTools(),
               ReasoningTools(think=True, analyze=True)],
        storage=load_local_storage(),
        description=dedent(AGENT_DEV_DESCRIPTION),
        instructions=dedent(AGENT_DEV_INSTRUCTION),
        additional_context=additional_context,
        markdown=True,
        add_datetime_to_instructions=True,
        add_history_to_messages=True,
        num_history_responses=3,
        read_chat_history=True,
        debug_mode=debug_mode,
    )
