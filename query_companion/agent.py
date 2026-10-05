import json
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseServerParams,
    StreamableHTTPServerParams,
)
from mcp import StdioServerParameters
from utils.settings import DEFAULT_MCP_SERVER_URL, DEFAULT_MCP_TOOLS

import warnings
warnings.filterwarnings("ignore",
                        category=DeprecationWarning,
                        module="google.cloud")

def _load_mcp_toolsets() -> list[MCPToolset]:
    raw_servers = os.getenv("MCP_SERVERS")
    if raw_servers is None:
        servers = [
            {
                "transport": "streamable_http",
                "url": os.getenv("MCP_SERVER_URL", DEFAULT_MCP_SERVER_URL),
                "tool_filter": DEFAULT_MCP_TOOLS,
            }
        ]
    else:
        try:
            servers = json.loads(raw_servers)
        except json.JSONDecodeError as error:
            raise ValueError("MCP_SERVERS must contain a JSON array.") from error

    if not isinstance(servers, list):
        raise ValueError("MCP_SERVERS must contain a JSON array.")

    toolsets = []
    for index, server in enumerate(servers):
        if not isinstance(server, dict):
            raise ValueError(f"MCP_SERVERS entry {index} must be a JSON object.")

        transport = server.get("transport", "stdio")
        if transport == "stdio":
            command = server.get("command")
            if not command:
                raise ValueError(
                    f"MCP_SERVERS entry {index} requires a 'command' for stdio."
                )
            connection_params = StdioServerParameters(
                command=command,
                args=server.get("args", []),
                env=server.get("env"),
            )
        elif transport == "sse":
            if not server.get("url"):
                raise ValueError(
                    f"MCP_SERVERS entry {index} requires a 'url' for SSE."
                )
            connection_params = SseServerParams(
                url=server["url"],
                headers=server.get("headers"),
            )
        elif transport == "streamable_http":
            if not server.get("url"):
                raise ValueError(
                    f"MCP_SERVERS entry {index} requires a 'url' for streamable HTTP."
                )
            connection_params = StreamableHTTPServerParams(
                url=server["url"],
                headers=server.get("headers"),
            )
        else:
            raise ValueError(
                f"Unsupported MCP transport {transport!r} in entry {index}."
            )

        toolsets.append(
            MCPToolset(
                connection_params=connection_params,
                tool_filter=server.get("tool_filter"),
            )
        )

    return toolsets


root_agent = Agent(
    name="query_companion",
    model="gemini-2.5-flash",
    description=(
        "Agent to answer questions over knowledge graphs."
    ),
    instruction=(
        """You are a helpful agent who can answer user
        questions over knowledge graphs. You should use the provided 
        tools to gather information and formulate accurate responses."""
    ),
    tools=_load_mcp_toolsets(),
)
