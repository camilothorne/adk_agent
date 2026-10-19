import os

DEFAULT_MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 
                                   "https://knowledge-graph-mcp-1098449730426.us-central1.run.app/mcp")

GEMINI_MODEL            = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Use this to filter the tools that are loaded from the MCP server. If None, all tools will be loaded.
# DEFAULT_MCP_TOOLS = None # Lists all tools from the MCP server
DEFAULT_MCP_TOOLS     = ["query_arxiv", 
                         "query_dblp_topic"] # Lists only the tools specified in this list. You can modify this list to include the tools you want to use.
