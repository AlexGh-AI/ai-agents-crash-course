import chainlit as cl
import dotenv
import os

from openai.types.responses import ResponseTextDeltaEvent

from agents import Runner, SQLiteSession
from nutrition_agent import nutrition_agent

dotenv.load_dotenv()
############################# Generate your chainlit Auh secret & update .env ###################
####### First: cd chatbot_complete           then type: chainlit create-secret 
#################################################################################################
################# To run this .py, first cd chatbot_complete, then chainlit run 4_authentication.py
#################################################################################################

#### Step 1: Initialize the memory
@cl.on_chat_start
async def on_chat_start():
    session = SQLiteSession("conversation_history")
    cl.user_session.set("agent_session", session)

#### Step 2: Use the memory by passing the session object
@cl.on_message
async def on_message(message: cl.Message):
    session = cl.user_session.get("agent_session")

    result = Runner.run_streamed(nutrition_agent, message.content, session=session)

    msg = cl.Message(content="")
    async for event in result.stream_events():
        # Stream final message text to screen
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(token=event.data.delta)

        elif (
            event.type == "raw_response_event"
            and hasattr(event.data, "item")
            and hasattr(event.data.item, "type")
            and event.data.item.type == "function_call"
            and len(event.data.item.arguments) > 0
        ):
            with cl.Step(name=f"{event.data.item.name}", type="tool") as step:
                step.input = event.data.item.arguments

    await msg.update()

########################################
## The next function will use chainlit Authentication with 
## username and password to allow access to our chatbot.
## We tell chainlit that this function is for auth by using the decorator @cl.password_auth_callback
## From the .env we obtain the username and password with os.getenv() & check for exact match
## to allow access to the chatbot, otherwise we deny access.
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
    
    ################################ Assignment 2 .chainlit\config.toml changes
    ###### to stop Autoscroll new user messages at the top of the window
   #####                                    user_message_autoscroll = false  
   ####    
   # and to change the Assistant's name 
   # # Name of the assistant.               name = "Assistant" changed it to "Nutrition Assistant Chatbot"