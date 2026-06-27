"""
Inspect an MCP server — lists all tools, resources, and prompts.
Usage:
  python sqlite_mcp/inspect.py
"""
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")


async def main():
    server_params = StdioServerParameters(command="python", args=[SERVER_PATH])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # --- Tools ---
            tools = await session.list_tools()
            print(f"\n TOOLS ({len(tools.tools)} found)")
            print("=" * 50)
            for t in tools.tools:
                params = list(t.inputSchema.get("properties", {}).keys())
                required = t.inputSchema.get("required", [])
                print(f"  {t.name}({', '.join(params)})")
                print(f"    {t.description}")
                if required:
                    print(f"    required: {required}")

            # --- Resources ---
            resources = await session.list_resources()
            print(f"\n RESOURCES ({len(resources.resources)} found)")
            print("=" * 50)
            for r in resources.resources:
                print(f"  {r.uri}")
                print(f"    {r.description or r.name}")

            # --- Prompts ---
            prompts = await session.list_prompts()
            print(f"\n PROMPTS ({len(prompts.prompts)} found)")
            print("=" * 50)
            if prompts.prompts:
                for p in prompts.prompts:
                    print(f"  {p.name} — {p.description}")
            else:
                print("  (none defined)")

            print()


if __name__ == "__main__":
    asyncio.run(main())
