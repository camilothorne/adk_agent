import os

# PROJECT_ID = os.getenv('PROJECT_ID', 'steel-wall-436909-g7')
# GEMINI_REGION = os.getenv('GEMINI_REGION', 'global')

DEFAULT_MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 
                                   "https://knowledge-graph-mcp-1098449730426.us-central1.run.app/mcp")
DEFAULT_MCP_TOOLS = ["query_dbpedia", 
                     "query_dblp_topic"]
