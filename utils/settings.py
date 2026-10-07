import os

# PROJECT_ID = os.getenv('PROJECT_ID', 'steel-wall-436909-g7')
# GEMINI_REGION = os.getenv('GEMINI_REGION', 'global')

DEFAULT_MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 
                                   "https://knowledge-graph-mcp-1098449730426.us-central1.run.app/mcp")

# Use this to filter the tools that are loaded from the MCP server. If None, all tools will be loaded.
DEFAULT_MCP_TOOLS = None
# DEFAULT_MCP_TOOLS = ["query_dbpedia",
#  		             "query_arxiv", 
#                      "query_dblp_topic"]
