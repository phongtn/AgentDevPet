import chainlit as cl

from main import wakeup_agent


@cl.on_chat_start
async def main():
    await cl.Message(content="Start new session").send()


@cl.on_message
async def main(message: cl.Message):
    agent = wakeup_agent()
    msg = cl.Message(content="")
    run_response = await agent.arun(message.content, stream=True)
    async for chunk in run_response:
        # yield chunk.content
        await msg.stream_token(chunk.content)

    await msg.update()

