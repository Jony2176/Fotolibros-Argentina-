
import asyncio
import os
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from dotenv import load_dotenv

load_dotenv()

async def test_agent():
    print("Testing Agent Tool Calling...")
    
    # Mock tool
    def my_tool():
        """Returns 'Tool correctly called'"""
        return "Tool correctly called"

    agent = Agent(
        model=OpenRouter(id="google/gemini-2.5-flash-lite"),
        tools=[my_tool],
        instructions=["You must call 'my_tool' immediately."],
        markdown=True
    )
    
    print("Sending prompt...")
    try:
        response = await agent.arun("Call your tool now.")
        print("Response received:")
        print(response.content)
        
        # Check logs/messages for tool calls if available
        # In Agno agent, usually tool calls are handled internally. 
        # We look for the result in the conversation or side effect.
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent())
