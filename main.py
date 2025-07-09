import os
import json
import re
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from form_tools import scrape_form_fields, get_knowledge_base_schema, query_knowledge_base
from form_filler import automate_form_filling

# --- 1. Define the State for our Graph ---
class AppState(TypedDict):
    form_url: str
    form_fields: List[Dict[str, Any]]
    kb_schema: dict
    query_map: dict
    final_form_data: dict

# --- 2. Define the Nodes of our Graph ---
def scrape_fields_node(state: AppState) -> dict:
    """Node to scrape the form fields from the URL."""
    print("--- Node: scrape_fields ---")
    form_url = state['form_url']
    fields = scrape_form_fields(form_url)
    return {"form_fields": fields}

def get_schema_node(state: AppState) -> dict:
    """Node to retrieve the knowledge base schema."""
    print("\n--- Node: get_schema ---")
    schema = get_knowledge_base_schema()
    return {"kb_schema": schema}

def generate_queries_node(state: AppState) -> dict:
    """Node that uses an LLM to map form fields to knowledge base queries."""
    print("\n--- Node: generate_queries ---")
    llm = ChatGroq(model="llama3-8b-8192", temperature=0.0)
    
    prompt = PromptTemplate(
        template="""
        Given the following list of form fields (with their types and options): 
        {fields}

        And the following knowledge base schema:
        {schema}

        Generate a JSON object mapping each field's 'label' to its precise dot-notation query path from the schema.
        For example, a field with label "Full Name" should map to "personal_info.full_name".
        A field with label "Do you require visa sponsorship?" should map to "custom_questions.requires_sponsorship".
        Output ONLY the raw JSON object.
        """,
        input_variables=["fields", "schema"]
    )
    
    chain = prompt | llm | StrOutputParser()
    
    response_str = chain.invoke({
        "fields": json.dumps(state['form_fields'], indent=2), 
        "schema": json.dumps(state['kb_schema'], indent=2)
    })
    
    try:
        # More robustly find the JSON object within the response string
        json_match = re.search(r'\{.*\}', response_str, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            query_map = json.loads(json_str)
            print("Successfully generated query map:")
            print(json.dumps(query_map, indent=2))
            return {"query_map": query_map}
        else:
            raise json.JSONDecodeError("No JSON object found in response", response_str, 0)
            
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response for query map: {e}")
        print(f"Raw response from LLM: '{response_str}'")
        return {"query_map": {}}

def execute_queries_node(state: AppState) -> dict:
    """Node to execute the generated queries and compile the final form data."""
    print("\n--- Node: execute_queries ---")
    final_data = {}
    if not state.get("query_map"):
        print("Query map is empty, skipping query execution.")
        return {"final_form_data": {}}

    for field_label, query in state['query_map'].items():
        answer = query_knowledge_base(query)
        final_data[field_label] = answer
    
    print("\nFinal data compiled:")
    print(json.dumps(final_data, indent=2))
    return {"final_form_data": final_data}

# --- 3. Build the Graph ---
def build_graph():
    """Builds and compiles the LangGraph workflow."""
    workflow = StateGraph(AppState)
    
    workflow.add_node("scrape_fields", scrape_fields_node)
    workflow.add_node("get_schema", get_schema_node)
    workflow.add_node("generate_queries", generate_queries_node)
    workflow.add_node("execute_queries", execute_queries_node)
    
    workflow.set_entry_point("scrape_fields")
    workflow.add_edge("scrape_fields", "get_schema")
    workflow.add_edge("get_schema", "generate_queries")
    workflow.add_edge("generate_queries", "execute_queries")
    workflow.add_edge("execute_queries", END)
    
    return workflow.compile()

# --- 4. Main Execution ---
def main():
    """Entry point of the application."""
    load_dotenv()
    
    form_path = os.path.abspath('job_form.html')
    form_url = f'file://{form_path}'
    
    initial_state = {"form_url": form_url}
    
    app = build_graph()
    final_state = app.invoke(initial_state)
    
    if final_state.get("final_form_data") and final_state.get("form_fields"):
        automate_form_filling(form_url, final_state["final_form_data"], final_state["form_fields"])
    else:
        print("\nGraph execution did not produce all necessary data. Aborting form fill.")

if __name__ == "__main__":
    main()
