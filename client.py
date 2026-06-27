"""
MCP Client — chat interface for the SQLite MCP server.
Uses Groq (free) with llama-3.1-8b-instant.

Setup:
  pip install mcp groq python-dotenv
  Copy .env from rag-study or set: export GROQ_API_KEY=your-key

Usage:
  python client.py

Then type questions like:
  - Show all users
  - What is alice's email?
  - Add user John, john@gmail.com, age 28, from Berlin
  - How many users are from London?
  - Show all orders with amount over 300
  - What did Bob order?
"""
import asyncio
import json
import os
from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load GROQ_API_KEY from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a helpful database assistant. You have access to a local SQLite
database with users and orders tables.

When the user asks a question:
- Use list_tables to see available tables
- Use describe_table to understand columns before writing queries
- Use run_query to answer questions with SELECT statements
- Use insert_user to add a new user
- Use insert_order to add an order for an existing user

Always present results in a clean, readable format. When showing user lists,
format them as a nice table or bullet list. Never expose raw JSON to the user."""


def mcp_tools_to_groq(mcp_tools) -> list:
    """Convert MCP tool definitions to Groq/OpenAI tool format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.inputSchema,
            }
        }
        for t in mcp_tools
    ]


async def main():
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_PATH]
    )

    print("Connecting to SQLite MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Auto-discover tools from the MCP server
            mcp_result = await session.list_tools()
            groq_tools = mcp_tools_to_groq(mcp_result.tools)

            print(f"Connected. Tools available: {[t['function']['name'] for t in groq_tools]}")
            print("-" * 50)
            print("SQLite Chat — type your question or 'quit' to exit")
            print("-" * 50)

            conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

            while True:
                try:
                    user_input = input("\nYou: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                conversation.append({"role": "user", "content": user_input})

                # Agentic loop — keep going until the model stops calling tools
                while True:
                    response = groq_client.chat.completions.create(
                        model=MODEL,
                        messages=conversation,
                        tools=groq_tools,
                        tool_choice="auto",
                        max_tokens=2048,
                    )

                    choice = response.choices[0]
                    message = choice.message

                    if choice.finish_reason == "stop":
                        print(f"\nAssistant: {message.content}")
                        conversation.append({"role": "assistant", "content": message.content})
                        break

                    if choice.finish_reason == "tool_calls":
                        # Add assistant message with tool_calls to history
                        conversation.append({
                            "role": "assistant",
                            "content": message.content or "",
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments,
                                    }
                                }
                                for tc in message.tool_calls
                            ]
                        })

                        # Execute each tool via MCP and collect results
                        for tc in message.tool_calls:
                            tool_name = tc.function.name
                            parsed = json.loads(tc.function.arguments) if tc.function.arguments else None
                            tool_args = parsed if isinstance(parsed, dict) else {}
                            print(f"  [tool: {tool_name}({json.dumps(tool_args)})]")

                            result = await session.call_tool(tool_name, tool_args)
                            result_text = result.content[0].text if result.content else "{}"

                            conversation.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": result_text,
                            })


if __name__ == "__main__":
    asyncio.run(main())
