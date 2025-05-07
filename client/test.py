import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Add project root directory to PATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv",  # Executable
    args=["run",
          "ffmpeg-tools"
          ],   # Optional command line arguments
    env=None,  # Optional environment variables
)

# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()
            print(f"prompts: {prompts}")

            # Get a prompt
            # prompt = await session.get_prompt(
            #     "analyze_ffmpeg_source", arguments={"path": "libswscale/options.c"}
            # )
            # print(f"prompt: {prompt}")

            # List available resources
            resources = await session.list_resources()
            print(f"resources: {resources}")

            resource_templates = await session.list_resource_templates()
            print(f"resource_templates: {resource_templates}")

            # List available tools
            tools = await session.list_tools()
            print(f"tools: {tools}")

            # import urllib.parse
            # Read a resource
            # content, mime_type = await session.read_resource("ffmpeg-source://")
            # print(f"content: {content}, mime_type: {mime_type}")

            # Call a tool
            result = await session.call_tool("get_ffmpeg_source_code", arguments={"path": "/libavfilter/src_movie.c"})
            print(f"result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())