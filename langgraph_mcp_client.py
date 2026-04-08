from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.messages import AIMessage,SystemMessage,AnyMessage, HumanMessage
from mcp_tool_client import tools
import os
import asyncio
# Define state
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
# define llm
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0.7)
# add tools to llm
llm_with_tools = llm.bind_tools(tools)
# Node
def chat_node(state: State):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": response}

# Build graph
builder = StateGraph(State)

builder.add_node("chat", chat_node)
builder.add_node('tools',ToolNode(tools))
builder.add_edge(START, "chat")
builder.add_conditional_edges(
    'chat',
    tools_condition,
)
builder.add_edge("tools", 'chat')


graph = builder.compile()

#system prompt
SYSTEM_PROMPT = """

You are an expert SQL assistant. Your job is to:
1. ALWAYS call `get_database_schema` tool FIRST before answering any question.
2. Use the schema to understand what tables and columns exist.
3. Convert natural language into valid SQLite SQL queries.
4. Execute queries using the `execute_sql_query` tool.
5. ALWAYS display the EXACT raw result returned by the tool to the user.

Rules:
- ALWAYS fetch schema first — never assume table/column names.
- NEVER answer from memory or make up data.
- NEVER say "query executed successfully" or "results retrieved" — always show the ACTUAL data.
- NEVER fabricate rows, names, or numbers.
- Format SELECT results as a clean markdown table.
- If the tool returns "No records found." — say exactly that.
- If the tool returns an error — show the error message.
- Only generate SELECT, INSERT, UPDATE, or DELETE statements.
- If the request is unclear, ask for clarification.
"""

# Runasync def main():
memory = None
async def main():
    global memory
    while True:
        user_input = input("Ask: ")
        if user_input.lower() in {"quit", "exit"}:
            break

        if memory is None:
            memory = {
                "messages": [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=user_input)
                ]
            }
        else:
            memory["messages"].append(HumanMessage(content=user_input))

        memory = await graph.ainvoke(memory)

        # Find the last AIMessage with non-empty text content
        # (avoids ToolMessage or AIMessage that only contains a tool_call with no text)
        result = ""
        for msg in reversed(memory["messages"]):
            if (
                isinstance(msg, AIMessage)
                and isinstance(msg.content, str)
                and msg.content.strip()
            ):
                result = msg.content.strip()
                break

        print(f"Assistant: {result if result else '(no text response)'}")
if __name__ == "__main__":
    asyncio.run(main())