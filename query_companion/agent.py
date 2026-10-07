import json
import logging
import os
import warnings
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseServerParams,
    StreamableHTTPServerParams,
)
from mcp import StdioServerParameters
from utils.settings import DEFAULT_MCP_SERVER_URL, DEFAULT_MCP_TOOLS

warnings.filterwarnings("ignore",
                        category=DeprecationWarning,
                        module="google.cloud")

logger = logging.getLogger(__name__)


class _NonTextPartsWarningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not (
            record.levelno == logging.WARNING
            and record.getMessage().startswith(
                "Warning: there are non-text parts in the response:"
            )
        )


logging.getLogger("google_genai.types").addFilter(_NonTextPartsWarningFilter())


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


mcp_toolsets = _load_mcp_toolsets()


async def list_available_tools() -> list[str]:
    names = []
    for toolset in mcp_toolsets:
        names.extend(tool.name for tool in await toolset.get_tools())
    return sorted(names)


def _log_llm_response(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> None:
    if llm_response.content is None:
        return

    response_text = "\n".join(
        part.text
        for part in llm_response.content.parts or []
        if part.text and not part.thought
    )
    if response_text:
        logger.info("LLM response: %s", response_text)


root_agent = Agent(
    name="query_companion",
    model="gemini-2.5-flash",
    description=(
        "Agent to answer questions over knowledge graphs."
    ),
    instruction=(
        """You are a helpful agent who can answer user
        questions over knowledge graphs. You should use the provided 
        tools to gather information and formulate accurate responses.
        MCP tool discovery is handled automatically. When asked to list the
        available tools, call `list_available_tools`. Do not call the MCP
        protocol method `list_tools` directly."""
    ),
    tools=[*mcp_toolsets, FunctionTool(list_available_tools)],
    after_model_callback=_log_llm_response,
)
