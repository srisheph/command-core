import os
import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from dotenv import load_dotenv
from graph import create_chat_graph
from openai import OpenAI
from openai.helpers import LocalAudioPlayer
import asyncio
from openai import AsyncOpenAI

load_dotenv()

openai=AsyncOpenAI()
MONGODB_URI = "mongodb://admin:admin@localhost:27017/langgraph?authSource=admin"
config={"configurable":{"thread_id":"thread_4"}}

def main():
     with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph=create_chat_graph(checkpointer=checkpointer)
        r=sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            r.pause_threshold=3

            while True:
                print("Say something!")
                audio=r.listen(source)
                print("Processing audio...")
                sst = r.recognize_google(audio)
                print("You said: " + sst)
                for event in graph.stream({"messages":[{"role":"user","content":sst}]},config,stream_mode="values"):
                    if "messages" in event:
                        event["messages"][-1].pretty_print()

# async def speak(text:str):
#         async with openai.audio.speech.with_streaming_response.create(
#             model="gpt-4o-mini-tts",
#             voice="coral",
#             input=text,
#             instructions="Agitated and stressed.",
#             response_format="pcm",
#         ) as response:
#             await LocalAudioPlayer().play(response)
    
main()
