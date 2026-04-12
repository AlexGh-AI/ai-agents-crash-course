import chainlit as cl
import dotenv

dotenv.load_dotenv()

##### Configuring the Chainlit: There is a .chainlit\config.toml for all chainlit configs.
#### From our COURSE_RESOURCES.md copy and paste the url for the UDEMY logo into the config.toml
#### file in the "logo_file_url" variable = https://upload.wikimedia.org/wikipedia/commons/e/e3/Udemy_logo.svg

##### The next decorated chainlit function will take a message and respond with the same message
##### To see this .py file open in your browser as a chatbot, open a terminal and type:
#####    cd chatbot_complete          then        chainlit run 1_simple_chatbot.py

@cl.on_message
async def on_message(message: cl.Message):
    await cl.Message(content=f"Received: {message.content}").send()
