from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.messages import AIMessage,SystemMessage,AnyMessage, HumanMessage
from mcp_tool_client import get_tools
import os
from dotenv import load_dotenv  
load_dotenv()  # Load environment variables from .env file
import asyncio
from pydantic import BaseModel
from fastapi import FastAPI,HTTPException
app = FastAPI(title="SQL Assistant API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# chat request
class ChatRequest(BaseModel):
    messages:str

# chat response
class ChatResponse(BaseModel):
    reply:str
    
# Define state
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# define llm
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0.7)

# system prompt 
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
# define graph and wrap in fastapi endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest): 
    if not request.messages.strip():
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")
    # get tool from mcp server
    tools =  await get_tools()
    
    #load tools in llm
    llm_with_tools = llm.bind_tools(tools)
    
    # define nodes
    def chat_node(state:State):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {'messages': response}
    #initialize graph
    builder = StateGraph(State)
    
    # add nodes
    builder.add_node("chat",chat_node)
    builder.add_node('tools',ToolNode(tools))
    # add edges
    builder.add_edge(START,'chat')
    builder.add_conditional_edges('chat',tools_condition)
    builder.add_edge('tools','chat')
    
    #execute graph
    graph = builder.compile()
    
    state = {"messages": [SystemMessage(content = SYSTEM_PROMPT), 
                          HumanMessage(content=request.messages)]}
    
    result_state = await graph.ainvoke(state) 
    reply= ""
    for msg in reversed(result_state["messages"]):
        if (isinstance(msg, AIMessage)
            and isinstance(msg.content, str)
            and msg.content.strip()
        ):
            reply = msg.content.strip()
            break
    return ChatResponse(reply=reply or 'no response generated')