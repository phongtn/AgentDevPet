
import uuid
from pprint import pprint

from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat

from devkit.agent_dev import build_agent

model =  OpenAIChat(id="gpt-4.1-mini")
agent = build_agent(model=model,
                    user_id="phong",
                    session_id="phong" + str(uuid.uuid1()),
                    debug_mode=False)
while True:
    user_input = input("You: ")
    if user_input.lower() == "/exit":
        break
    if user_input.lower() == "/generate":
        print("Waiting for user input...")
        continue
    agent.print_response(user_input)
    agent.get_messages_for_session()
    # pprint(agent.get_messages_for_session())