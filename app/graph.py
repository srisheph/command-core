import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

load_dotenv()


class State(TypedDict):
    messages:Annotated[list,add_messages]


@tool
def write_file(filename: str, content: str):
    """Save code into a file inside chat_gpt folder."""
    os.makedirs("chat_gpt", exist_ok=True)
     # remove any folder path user/model sends
    filename = os.path.basename(filename)
    path = os.path.join("chat_gpt", filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File written successfully to {path}"

@tool
def run_command(cmd:str):
    """Takes a command line prompt and executes it on the user's machine and
       returns the result of the command.

       Example:
       run_command(cmd="dir") where dir is a command to list the contents of the current directory on Windows.
    """
    result=os.system(cmd)
    return result



llm=init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools=llm.bind_tools(tools=[run_command,write_file])

def chatbot(state:State) :
    system_prompt=SystemMessage(content="""
You are an AI coding assistant.

The user is running on WINDOWS CMD (not Linux or Mac).
So:
- Use Windows commands only (dir, mkdir, type, echo, copy, del)
- NEVER use ls, cat, touch, or <<EOF
- When listing files use: dir

When saving code:
- Use the write_file tool (not shell redirection)
- Always save files inside chat_gpt folder.
                                
You are an AI that always saves any generated code into a file automatically using the write_file tool.
Do not ask for permission. Always create a file with a meaningful name.

""")
    message = llm_with_tools.invoke([system_prompt]+state["messages"])
    # assert len(message) <= 1
    return {"messages": [message]}

tool_node=ToolNode(tools=[run_command,write_file])
graph_builder=StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("tools",tool_node)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools","chatbot")
# graph_builder.add_edge("chatbot",END)

# 

def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)
