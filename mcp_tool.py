import json
from crewai.tools import BaseTool
from mcp_server import MCPServer

class MCPKnowledgeBaseTool(BaseTool):
    name: str = "MCP Knowledge Base Query"
    description: str = (
        "Use this tool to retrieve specific, structured information about the user. "
        "Your query must be a precise, dot-notation path to the data you need. "
        "For example, to get the user's email, the query should be 'personal_info.email'."
    )

    # Instantiate the server when the tool is created
    _mcp_server: MCPServer = MCPServer(kb_path='user_data.json')

    def _run(self, query: str) -> str:
        """Queries the knowledge base and returns the result as a string."""
        print(f"\n[MCP Tool] Running query: {query}")
        result = self._mcp_server.fetch_info(query)

        # Ensure the tool's output is always a string for the LLM
        if result is None:
            return "No information found for that query."
        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2)
        return str(result)