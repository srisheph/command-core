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

openai_client=AsyncOpenAI()

MONGODB_URI = "mongodb://admin:admin@localhost:27017/langgraph?authSource=admin"
config={"configurable":{"thread_id":"thread_4"}}

async def generate_summary(action_report:str):
    summary_prompt=f"""
Summarize the following action report in 1-2 sentences in response to the user's query.
Focus on what actions the assistant performed.

Details:
{action_report}
""".strip()
    
    resp = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
    )
    return resp.choices[0].message.content.strip()

async def speak(text:str):

        async with openai_client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
            instructions="Positive and a cheerful tone",
            response_format="pcm",
        ) as response:
            await LocalAudioPlayer().play(response)

async def main():
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

                final_message=None
                
                for event in graph.stream({"messages":[{"role":"user","content":sst}]},config,stream_mode="values"):
                    if "messages" in event:
                        msg=event["messages"][-1]
                        msg.pretty_print()
                        final_message=msg

                if final_message and getattr(final_message,"content",None):
                    assistant_response=final_message.content

                    action_report=f"""
                    User Query: {sst}
                    Assistant Response: {assistant_response}
                    """.strip()

                    summary = await generate_summary(action_report)
                    print("Summary:", summary)
                    await speak(summary)
                        

if __name__=="__main__":
    asyncio.run(main())