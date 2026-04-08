from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
async def get_tools():
    client = MultiServerMCPClient(
        {
            'My_MCP_Server': {
                'url': 'http://127.0.0.1:8000/sse',
                'transport': 'sse',
            }
        })
    tools = await client.get_tools()
    for tool in tools:
        print(f'fetched {len(tools)} tool: {[t.name for t in tools]}')
    return tools
tools = asyncio.run(get_tools())


