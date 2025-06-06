import uuid

from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat
from qdrant_client.http import model

from devkit.agent_dev import build_agent


def wakeup_agent():
    model = OpenAIChat(id="gpt-4.1-mini")
    # model=DeepSeek()
    return build_agent(model=model,
                       user_id="phong",
                       session_id="phong" + str(uuid.uuid1()),
                       debug_mode=False)


def chat_with_agent(agent):
    """
    Manages an interactive chat session with the provided agent.

    The loop continues until the user types '/exit'.
    If the user types '/generate', it prompts for more input.
    Otherwise, it sends the input to the agent and displays the response.

    Args:
        agent: An agent object with 'print_response' and 'get_messages_for_session' methods.
    """
    print("Hello boss. Type '/e' to end.")
    while True:
        user_input = input("You: ")

        if user_input.lower() == "/e":
            print("Bye Boss.")
            break

        if user_input.lower() == "/generate":
            print("Waiting for user input...")
            continue

        agent.print_response(user_input, stream=True)
        # messages = agent.get_messages_for_session()


if __name__ == '__main__':
    agent = wakeup_agent()
    chat_with_agent(agent)