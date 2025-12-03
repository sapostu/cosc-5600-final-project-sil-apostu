import os
import json
import requests

class CommonUtil:
    
    @staticmethod
    def _get_api_key(config_path=None):
        # Retrieves the API key from environment variable or config file
        
        # Check environment variable 
        env_key = os.environ.get("OPENROUTER_API_KEY")
        if env_key:
            return env_key

        # Check config file
        if config_path is None:
            config_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "config.json")
            )

        try:
            # Load config file
            with open(config_path, "r", encoding="utf-8") as fh:
                
                # Parse JSON
                cfg = json.load(fh)
                key = cfg.get("OPENROUTER_API_KEY") or cfg.get("api_key")
                
                # Return key if found
                if key:
                    return key
        
        # Errors below
        except FileNotFoundError:
            pass
        
        except Exception:
            pass

        raise RuntimeError(
            "API key not found. Set OPENROUTER_API_KEY env var or create config.json with OPENROUTER_API_KEY."
        )

    @staticmethod
    def callLLM(api_key, prompt):
        # Wrapper function to call the LLM API

        # Model to use
        model="google/gemini-2.0-flash-001"

        # OpenRouter API URL
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Headers with API key
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Data with model and prompt
        data = {"model": model, "messages": [{"role": "user", "content": prompt}]}

        # Model above from OpenRouter AI API was chosen for being cheap, performant, and non-reasoning
        #
        # Non-reasoning speeds things up a lot from my own testing
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        
        # Raise for status
        resp.raise_for_status()
        
        # Return content
        return resp.json()["choices"][0]["message"]["content"]

    @staticmethod
    def verify_dataset_test_obj_fields(obj):
        # Verifies that the fields defined the list, all within DatasetTestObj 
        #   are set (not None or null/empty for strings/lists)
        #
        # Returns True if all are set, otherwise False.
        
        # All required fields we want to make sure are set
        required_fields = [
            "sort_id",
            "dev_db_id",
            "dev_db_path",
            "dev_question",
            "dev_gold_sql",
            "rag_examples",
            "schema_string",
            "schema_linking_tables"
        ]
        
        # Loop
        for field in required_fields:
            
            # Loop through each required field, get the field then check each field
            value = getattr(obj, field, None)

            # Check for None, empty string, or empty list
            if value is None:
                print(f"Field {field} is None")
                return False

            # Check for empty string or empty list
            if isinstance(value, str) and not value.strip():
                print(f"Field {field} is an empty string")
                return False
            
            # Check for empty list
            if isinstance(value, list) and not value:
                print(f"Field {field} is an empty list")
                return False
        
        # All fields are set
        return True
