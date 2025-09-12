import uuid
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.base import Model
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools
from agno.tools.giphy import GiphyTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.shell import ShellTools

from .prompt import AGENT_DEV_DESCRIPTION, AGENT_DEV_INSTRUCTION
from .tools.pexels import PexelsTools


def init_local_storage():
    return SqliteDb(
        db_file="data.db",
        memory_table="memories"
    )


def build_agent(
        model: Model,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = True,
) -> Agent:


    return Agent(
        name="DEV-PET",
        user_id=user_id,
        session_id=session_id,
        model=model,
        db=init_local_storage(),
        tools=[
            DuckDuckGoTools(),
            ShellTools(),
            PexelsTools(),
            FileTools()
        ],
        description=dedent(AGENT_DEV_DESCRIPTION),
        instructions=dedent(AGENT_DEV_INSTRUCTION),
        add_history_to_context=True,
        num_history_runs=3,
        enable_agentic_memory=True,
        markdown=True,
        read_chat_history=True,
        debug_mode=debug_mode,
    )


def wakeup_agent():
    model = OpenAIChat(id="gpt-4.1-mini")
    return build_agent(model=model,
                       user_id="John",
                       session_id=str(uuid.uuid1()),
                       debug_mode=True)