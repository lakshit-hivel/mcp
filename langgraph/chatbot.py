from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import MemorySaver
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import ToolMessage
from typing import Annotated
import asyncio
from langchain_core.messages import SystemMessage
from messages import BOT_SYSTEM_MESSAGE

# Maximum number of messages to keep in history (excluding system message)
MAX_MESSAGES = 10

load_dotenv()

server_params = StdioServerParameters(
    command="python",
    args=["/Users/lakshitagarwal/Hivel/mcp-server/pr_mcp_server.py"], 
    env=None
)

mcp_client = None
mcp_session = None
mcp_tools = None

async def init_mcp():
    """Initialize MCP connection and load tools"""
    global mcp_client, mcp_session, mcp_tools
    
    # Create client
    mcp_client = stdio_client(server_params)
    read, write = await mcp_client.__aenter__()
    
    # Create session
    mcp_session = ClientSession(read, write)
    await mcp_session.__aenter__()
    await mcp_session.initialize()
    
    # Load tools
    mcp_tools = await load_mcp_tools(mcp_session)
    for tool in mcp_tools:
        print(tool.name)
    
    return mcp_tools

# System message to guide the LLM on how to use database tools
system_message = SystemMessage(content=BOT_SYSTEM_MESSAGE)

# Will be initialized in main()
tools = []
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = None

# state
class chatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    summary: str




def create_summary(messages: list[BaseMessage]) -> str:
    """Create a summary of the messages"""
    conversation = "\n".join([
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content[:200]}"
        for m in messages 
        if hasattr(m, 'content') and not isinstance(m, SystemMessage)
    ])
    prompt = f"Summarize this conversation in 2-3 sentences:\n{conversation}"
    summary = llm.invoke([HumanMessage(content=prompt)])
    return summary.content



# Node functions
def chat_node(state: chatState) -> chatState:
    global llm_with_tools
    messages = state["messages"]
    
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [system_message] + messages
    
    if len(messages) > MAX_MESSAGES + 1: 
        old_messages = messages[1:-(MAX_MESSAGES-3)] 
        recent_messages = messages[-(MAX_MESSAGES-3):]

        summary = create_summary(old_messages)
        summary_msg = SystemMessage(content=f"Previous conversation: {summary}")
        messages = [messages[0], summary_msg] + recent_messages

        state["summary"] = summary

    
    res = llm_with_tools.invoke(messages)
    return {"messages": [res]}

async def tool_node(state: chatState) -> chatState:
    """Execute any tool calls from the last message"""
    last_message = state["messages"][-1]
    
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": []}
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        # Find the matching tool
        matching_tool = None
        for tool in tools:
            if tool.name == tool_call["name"]:
                matching_tool = tool
                break
        
        if matching_tool:
                result = await matching_tool.ainvoke(tool_call["args"])
                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    )
                )
        else:
            # Tool not found - still need to respond to maintain message flow
            tool_messages.append(
                ToolMessage(
                    content=f"Error: Tool '{tool_call['name']}' not found",
                    tool_call_id=tool_call["id"]
                )
            )
    return {"messages": tool_messages}

def should_continue(state: chatState) -> str:
    """Decide: continue to tools or end?"""
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "end"


async def main():
    """Main async function to initialize and run the chatbot"""
    global tools, llm_with_tools

    tools = await init_mcp()
    llm_with_tools = llm.bind_tools(tools)
    
    checkptr = MemorySaver()
    
    graph = StateGraph(chatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)
    
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges(
        "chat_node",
        should_continue,
        {
            "tools": "tools",
            "end": END
        })
    graph.add_edge("tools", "chat_node")
    
    workflow = graph.compile(checkpointer=checkptr)
    
    thread_id = '6785'
    
    while True:
        user_inp = input("You: ")
        if user_inp in ["exit", "bye", "quit"]:
            break
    
        config = {"configurable": {"thread_id": thread_id}}
        res = await workflow.ainvoke({"messages": [HumanMessage(content=user_inp)]}, config=config)
        print(f"LLM: {res['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
