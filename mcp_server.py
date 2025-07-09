import json
from typing import Any, Dict
from knowledge_base import KnowledgeBase

class MCPServer:
    """
    Simulates the Model-Context Protocol server logic.
    It uses the KnowledgeBase to retrieve information based on queries.
    """
    def __init__(self, kb_path: str):
        self.kb = KnowledgeBase(kb_path)

    def fetch_info(self, query: str) -> Any:
        """
        Retrieves information from the knowledge base based on a simple query.

        Example queries:
        - "personal_info.full_name"
        - "work_experience[0].job_title"
        - "skills.programming_languages"
        """
        # Clean the query string to remove extra quotes or spaces from the LLM output.
        cleaned_query = query.strip().strip("'\"")

        print(f"\n[MCP] Received query: '{cleaned_query}'")
        try:
            # Simple dot-notation and index-based query engine
            keys = cleaned_query.replace("]", "").replace("[", ".").split('.')
            value = self.kb.get_all_data()
            for key in keys:
                if key.isdigit():
                    value = value[int(key)]
                else:
                    value = value[key]
            
            # Pretty print the result if it's a dictionary or list
            if isinstance(value, (dict, list)):
                print("[MCP] Found data:")
                print(json.dumps(value, indent=2))
            else:
                 print(f"[MCP] Found data: {value}")

            return value
        except (KeyError, IndexError, TypeError):
            print(f"[MCP] Could not find data for query: '{cleaned_query}'")
            return None
        except Exception as e:
            print(f"[MCP] An error occurred during query execution: {e}")
            return None


def test_mcp_server():
    """
    Tests the MCPServer by creating an instance and running several queries.
    """
    mcp = MCPServer(kb_path='user_data.json')

    # --- Test Queries ---
    mcp.fetch_info("personal_info.email")
    mcp.fetch_info("work_experience[0].company")
    mcp.fetch_info("skills.frameworks")
    mcp.fetch_info("custom_questions.requires_sponsorship")
    mcp.fetch_info("education[0]")
    mcp.fetch_info("invalid.query.path") # Test invalid query

if __name__ == "__main__":
    test_mcp_server()
