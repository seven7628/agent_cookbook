from langgraph.types import interrupt
from langgraph.prebuilt import create_react_agent

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
import asyncio


client = MultiServerMCPClient(
    {
        "math": {
            "command": "/opt/homebrew/anaconda3/envs/zyptorch/bin/python",
            "args": [
                "/Users/zyp/Desktop/QXLLM/MCPText/langgraph-cookbook/math_mcp.py",
            ],
            "transport": "stdio"
        }
    }
)

# 定义一个异步函数来获取工具
async def get_tools_async():
    return await client.get_tools()

llm = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434")

# 由于无法直接调用异步函数，这里需要假设在合适的异步上下文中调用
# 这里只是示例，实际使用时需要在 async 函数中调用
# 这里简单模拟获取工具
tools = asyncio.run(get_tools_async())
agent = create_react_agent(
    llm,
    tools
)

# 定义一个异步函数来调用 agent.ainvoke
# async def call_agent_async():
#     math_response = await agent.ainvoke(
#     {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
# )

#     print(math_response)

# asyncio.run(call_agent_async())

math_response = agent.invoke({"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]})
print(math_response)