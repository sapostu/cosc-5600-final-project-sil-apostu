import sqlite3
import json
import ast
import time
import re
from typing import Any
from Util.CommonUtil import CommonUtil

class SchemaUtil:
    
    @staticmethod
    def extract_schema_from_sqlite(db_path):
        # Need to get schema from files given a db_path

        # Connect to .sqlite file
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
        tables = [row[0] for row in cursor.fetchall()]

        # Build schema string; will return this
        schema_lines = ["Tables and Columns:"]

        # Get columns for each table
        for table in tables:
            
            # Add table name found
            schema_lines.append(f"\nTable: {table}")

            # Get columns for each table with use of PRAGMA
            cursor.execute(f"PRAGMA table_info('{table}')")
            columns = cursor.fetchall()

            # Add columns for each table
            for col in columns:
                col_name = col[1]
                schema_lines.append(f" - {table}.{col_name}")

        # Close connection and return
        conn.close()
        return "\n".join(schema_lines)

    @staticmethod
    def get_schema_linking_prompt(dev_question, schema_text):
        # Decoupled function that takes care of prompt used and sent to LLM api

        return f"""
You are performing Schema Linking for a Text-to-SQL system.

Schema Linking = select ONLY the tables and columns from the schema that
are relevant to answering the question.

Follow the style of Divide-and-Prompt and Open-SQL used in the industry:
directly output the relevant schema items. Here is the relevant information between the dotted $$$$$ lines.

$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

( Question below)
{dev_question}

( Full Database Schema below)
{schema_text}

$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

IMPORTANT INFORMATION:
- Return ONLY a Python list of strings. No other text or formatting.
-No markdown.
-No backticks.
-No explanations.
-Just the JSON list.

( Example below)
["table.column", "table.column"]

Return the list now:
"""

    @staticmethod
    def try_parse_schema_linking_output(raw, retries=5):
        # Extract a schema linking list from inconsistent LLM output

        def _attempt_once(raw_input):

            # Will list cases I am testing for and a example of what I am looking for

            # Already a Python list
            #
            #   ["table.colA", "table.colB"]
            #   ['x', 'y', 'z']

            if isinstance(raw_input, list):
                return [str(x).strip() for x in raw_input]

            # Not a string so cannot parse
            #
            #   None
            #   123

            if not isinstance(raw_input, str):
                return None

            text = raw_input.strip()

            # Excessive ``` characters from LLM output
            #
            #   ```json
            #   ["col1", "col2"]
            #   ```
            #   ```["col1","col2"]```

            if text.startswith("```"):
                text = text.strip("`")
                text = text.replace("json", "", 1).strip()


            # Crop to the first JSON/Python list or object found in the text
            #
            #   "Here is your list: ['A','B']"
            #   "Relevant columns: [\"x\", \"y\"] and more..."

            first_token = min(
                [index for index in (text.find("["), text.find("{")) if index != -1],
                default=None
            )
            if first_token is not None:
                text = text[first_token:].strip()

            # Try generic JSON parsing here
            #
            #   ["a", "b", "c"]
            #   [ "id" , "name" ]

            try:
                parsed = json.loads(text)

                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed]

            except Exception:
                pass

            # Fix single-quotes into double-quotes for valid JSON
            #
            #   ['a', 'b']
            #   ['table.colA', 'table.colB']

            try:
                fixed = text.replace("'", '"')
                parsed = json.loads(fixed)

                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed]

            except Exception:
                pass

            # Python 'literal' type list, ast.literal_eval() lets us check for literals
            #
            #   ['a','b','c']
            #   ["x","y"]
            #   ['weird value with "quotes" inside']

            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed]
            except Exception:
                pass

            # Extract the first substring found between these characters: \[ and \] and parse that
            #
            #   "Model returned: result = [\"A\", \"B\", \"C\"] DONE"
            #   "Something broke, but here's a list: [1, 2, 3]"

            match = re.search(r"(\[[^\]]*\])", text, flags=re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed]
                except Exception:
                    pass

            # If you got here, you failed; retry
            return None

        # Try multiple times if earlier attempts fail
        for _ in range(retries):
            result = _attempt_once(raw)
            if result is not None:
                return result

        return None

    @staticmethod
    def schema_linking(api_key, schema_text, dev_question):
        
        # Get prompt
        prompt = SchemaUtil.get_schema_linking_prompt(dev_question, schema_text)

        # Try multiple times, needed since LLM is not always consistent
        attempts = 25

        # Loop
        for i in range(attempts):

            print(f"[Schema Linking] Attempt {i+1} of {attempts}...")

            # Call LLM
            raw = CommonUtil.callLLM(api_key, prompt)
            parsed = SchemaUtil.try_parse_schema_linking_output(raw)

            # Check type
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed]

            # Wait 0.5 seconds for LLM rate limit
            time.sleep(0.5)

        raise RuntimeError(
            # Found error
            f"Schema linking failed after {attempts} attempts.\nLast raw output:\n{raw}"
        )
