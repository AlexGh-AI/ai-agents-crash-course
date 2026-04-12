import chainlit as cl
import dotenv

from openai.types.responses import ResponseTextDeltaEvent

from agents import Runner, SQLiteSession  ### SQLiteSession is needed for local file based memory
from nutrition_agent import nutrition_agent

dotenv.load_dotenv()

#################################################################################################
################# To run this .py, first cd chatbot_complete, then chainlit run 3_memory.py
#################################################################################################

########################################################################
########## Implementing memory with OpenAI SDK is a 2 step process:
########## 1. Initialize the memory (as in on_chat_start() below)
########## 2. Use the memory by passing the session object.(as in on_message() parts A and B)
########################################################################


#### Step 1: Initialize the memory
@cl.on_chat_start ####### decorator, everytime the chat starts it initializes a memory for it
async def on_chat_start():
    session = SQLiteSession("conversation_history") ### converstion_history is file name for memory
    cl.user_session.set("agent_session", session) ### we name our memory agent_session

#### Step 2: Use the memory by passing the session object
@cl.on_message
async def on_message(message: cl.Message):

    # A) Get the initialized memory (agent_session)
    session = cl.user_session.get("agent_session") 

    # B) Everytime you use Runner from now on, pass it your session= object/memory
    result = Runner.run_streamed(nutrition_agent, message.content, session=session) 

    msg = cl.Message(content="")
    async for event in result.stream_events():
        # Stream final message text to screen

        ###################################################
        ####### The if section is for streaming tokens/text
        ####### and the elif section is for tools.
        ####################################################
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
