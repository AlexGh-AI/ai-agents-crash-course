import chainlit as cl
import dotenv
from openai.types.responses import ResponseTextDeltaEvent ### Need this for streaming

from agents import Runner
from nutrition_agent import nutrition_agent

dotenv.load_dotenv()
################### To run this chatbot. open a terminal, cd to your chatbot_complete folder. type:
###################           chainlit run 2_agentic_chatbot.py



##################### The next async function will implement our streaming feature.
##################### Uses Runner.run_streamed() instead of Runner.run() 
@cl.on_message
async def on_message(message: cl.Message):

    result = Runner.run_streamed(
        nutrition_agent,
        message.content,
    )

    msg = cl.Message(content="")
    async for event in result.stream_events():
        ###########################################################################################
        ################################# IMPORTANT if and elif sections below ####################
        ###########################################################################################
        # Stream final message text to screen
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(token=event.data.delta)
            print(event.data.delta, end="", flush=True)
        # the elif section catches the tool calls, 
        # while the if above section catches regular streamed tokens/text from LLM
        elif (
            event.type == "raw_response_event"
            and hasattr(event.data, "item")
            and hasattr(event.data.item, "type")
            and event.data.item.type == "function_call"
            and len(event.data.item.arguments) > 0
        ):
            #################################################################
            ################# The new Chainlit concept: Step
            ################# It adds status to the response
            #################################################################
            with cl.Step(name=f"{event.data.item.name}", type="tool") as step:
                step.input = event.data.item.arguments
                #################### print to the console next(For Debugging, not UI)
                print(
                    f"\nTool call: {
                        event.data.item.name} with args: {
                        event.data.item.arguments}"
                )

    await msg.update() ### closes the msg
