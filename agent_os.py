from agno.os import AgentOS

from devkit.agent_dev import wakeup_agent
from devkit.agent_team import reasoning_finance_team

agent = wakeup_agent()
agent_os = AgentOS(
    os_id="agent-os",
    description="AgentOS",
    agents=[agent],
    teams=[reasoning_finance_team]
)
app = agent_os.get_app()
if __name__ == "__main__":
    agent_os.serve(app="agent_os:app", reload=True)