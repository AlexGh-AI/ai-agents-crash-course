import os
##################################################################################################
# This is our chainlit Chatbot UI. It uses the production ready(guardrails,Authentication) 
# multi-agentic nutrition agent and meal advisor of nutrition_agent.py in this multi_agent_chatbot
# folder.
##################################################################################################
# NOTE: Due to deployment issues to Render.com with the original requirements.txt caused by the 
# pinned package versions in it, i used claude's help to minimize the entries and not specifying 
# package versions. Render deployment error logs state that Render is using Python 3.14 (python3.14) 
# which is too new and bleeding edge. pydantic_core can't build because it needs Rust/Cargo and 
# the filesystem is read-only on Render.
# You need to force Render to use Python 3.11 or 3.12. 
##################################################################################################
import chainlit as cl
import dotenv
from agents import InputGuardrailTripwireTriggered, Runner, SQLiteSession
from nutrition_agent import exa_search_mcp, nutrition_agent
from openai.types.responses import ResponseTextDeltaEvent

dotenv.load_dotenv()


@cl.on_chat_start
async def on_chat_start():
    session = SQLiteSession("conversation_history")
    cl.user_session.set("agent_session", session)
    # This is the only change in this file compared to the chatbot/agentic_chatbot.py file
    await exa_search_mcp.connect()


@cl.on_message
async def on_message(message: cl.Message):
    session = cl.user_session.get("agent_session")

    result = Runner.run_streamed(
        nutrition_agent,
        message.content,
        session=session,
    )

    msg = cl.Message(content="")
    async for event in result.stream_events():
        # Stream final message text to screen
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(token=event.data.delta)
            print(event.data.delta, end="", flush=True)

        elif (
            event.type == "raw_response_event"
            and hasattr(event.data, "item")
            and hasattr(event.data.item, "type")
            and event.data.item.type == "function_call"
            and len(event.data.item.arguments) > 0
        ):
            with cl.Step(name=f"{event.data.item.name}", type="tool") as step:
                step.input = event.data.item.arguments
                tool_name = event.data.item.name
                tool_args = event.data.item.arguments
                print(f"\nTool call: {tool_name} with args: {tool_args}")
                # print(
                #     f"\nTool call: {
                #         event.data.item.name} with args: {
                #         event.data.item.arguments}"
                # ) # commented because of deploy error with python 3.11 based on Claude's suggestion

    await msg.update()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == (
        os.getenv("CHAINLIT_USERNAME"),
        os.getenv("CHAINLIT_PASSWORD"),
    ):
        return cl.User(
            identifier="Student",
            metadata={"role": "student", "provider": "credentials"},
        )
    else:
        return None
