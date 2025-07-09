import json
from typing import Dict, Any
from pydantic import BaseModel, ValidationError

class KnowledgeBase:
    """
    Handles loading and accessing the structured user data from a JSON file.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Loads the data from the specified JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                print("Knowledge base loaded successfully.")
                return data
        except FileNotFoundError:
            print(f"Error: The file at {self.file_path} was not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: The file at {self.file_path} is not a valid JSON file.")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while loading the knowledge base: {e}")
            return {}

    def get_all_data(self) -> Dict[str, Any]:
        """Returns all data from the knowledge base."""
        return self._data

# Pydantic models for validation (optional but good practice)
class PersonalInfo(BaseModel):
    full_name: str
    email: str

# You can define more models for other sections like WorkExperience, Education etc.

def validate_data(data: Dict[str, Any]):
    """Validates the structure of the loaded data."""
    try:
        PersonalInfo(**data.get("personal_info", {}))
        print("Personal info data is valid.")
    except ValidationError as e:
        print(f"Data validation error: {e}")