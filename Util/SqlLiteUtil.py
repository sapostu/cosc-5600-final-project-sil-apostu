from datetime import time
import os
import time
import sqlite3
import re

from Util.CommonUtil import CommonUtil

class SqlLiteUtil:
    
    @staticmethod
    def load_sqlite_databases(dataset_name, base_path = "Dataset"):
        
        # Sanitize dataset name
        dataset_name = dataset_name.lower().strip()

        # Choose only from allowable datasets
        if dataset_name not in {"bird", "spider-1.0"}:
            raise ValueError(f"Unknown dataset '{dataset_name}'. Expected 'bird' or 'spider-1.0'")

        # Find folder
        dev_db_root = os.path.join(base_path, dataset_name, "dev_databases")
        if not os.path.exists(dev_db_root):
            raise FileNotFoundError(f"dev_databases folder not found at: {dev_db_root}")

        # Hashmap: KEY db_id, VALUE  db_path
        db_map = {}
        
        # Walk through folder to find all .sqlite files
        for root, dirs, files in os.walk(dev_db_root):
            
            # Loop through files
            for file in files:
                
                # If sqlite file, add to map
                if file.endswith(".sqlite"):
                    
                    # Get db_id and path
                    db_id = os.path.basename(root)

                    # Full path
                    db_path = os.path.join(root, file)
                    
                    # Verify database file is readable
                    try:
                        # Check file before adding to map then close
                        conn = sqlite3.connect(db_path)
                        conn.close()

                    except Exception as e:
                        # There was an error opening the .sqlite file
                        #
                        # Continue and count this in eval metrics
                        
                        # Warn then continue
                        print(f"[WARN] Failed to open {db_id} at {db_path}: {e}")
                        continue
                    
                    # Add to map
                    db_map[db_id] = db_path

        # If no databases found, raise error
        if len(db_map) == 0:
            raise RuntimeError(f"No .sqlite databases found for dataset '{dataset_name}'")
        
        # Return map from earlier
        return db_map

    @staticmethod
    def run_sql_query(query, db_path):
        # Run SQL query on a given .sqlite file

        # Strip query   
        query = query.strip()

        # Connect to .sqlite file
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Try to execute query
        try:
            # Execute query
            cur.execute(query)

            # Fetch all rows    
            rows = cur.fetchall()

            # Convert rows to list of tuples
            result = [tuple(row) for row in rows]

            # Return result
            return result

        except Exception as e:
            # Error here
            
            # Print and return
            print(f"[ERROR] SQL failed on DB '{db_path}': {e}")
            return None

        finally:
            # Close connection; finish with the current .sqllite file at the moment
            conn.close()

    @staticmethod
    def getPrompt(obj, few_shot_block, linked_schema_str):
        #Builds the SQL generation LLM prompt from object fields, few-shot string, and linked schema string
        
        return f"""
You are a professional Text-to-SQL model. 
Your task is to convert natural language questions into SQL queries.

RULES:
- Use ONLY tables/columns appearing in the Schema Linking List.
- Use the RAG few-shot examples for guidance on SQL structure.
- Use the Full Schema only for table/column validation.
- Return ONLY the SQL query. No markdown. No explanation.

Here is the relevant information between the dotted $$$$$ lines.

$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

( Question below )
{obj.dev_question}

( Schema Linking List below )
{linked_schema_str}

( Full Schema Reference below )
{obj.schema_string}

( FEW SHOT EXAMPLES (RAG) below )
{few_shot_block}

$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

NOW RETURN ONLY THE SQL QUERY:
"""

    @staticmethod
    def generate_sql_for_obj(
        obj,
        api_key
    ):
        # Creates an SQL query for one dataset object
        #
        # Uses RAG examples, schema linking, and an LLM
        #
        # Retries a few times if the model gives bad output
        #
        # Build few-shot examples in a readable block

        # Init variable
        few_shot_block = ""
        
        # Set max retries
        max_retries = 25

        # If there are rag examples, add
        if obj.rag_examples:
            # Store rag examples in a list
            parts = []

            # Loop through each rag example, add to list
            for ex in obj.rag_examples:

                # Get question and sql
                q = ex.get("question", "")
                sql = ex.get("sql", "")

                # Add to list with desired formatting
                parts.append(f"### Example\nQuestion: {q}\nSQL: {sql}")

            # Join list into a string
            few_shot_block = "\n\n".join(parts)

        # Pick out only the columns/tables the linker flagged as relevant
        #
        # Create failsafe string if no schema linking tables found
        linked_schema_str = (
            "\n".join(obj.schema_linking_tables)
            if obj.schema_linking_tables
            else "-- NONE FOUND --"
        )

        # Build the full prompt the LLM will use; remove whitespace and trailling characters
        prompt = SqlLiteUtil.getPrompt(obj, few_shot_block, linked_schema_str)
        obj.llm_prompt = prompt.strip()

        # Init raw output of llm variable for later
        last_raw = None

        # Try calling the LLM a few times in case the first output is messy
        for attempt in range(1, max_retries + 1):
            # Print attempt number and object id
            print(f"[SQL Generation] Attempt {attempt}/{max_retries} for Obj {obj.sort_id}...")

            # Call LLM
            raw = CommonUtil.callLLM(api_key, obj.llm_prompt)

            # If no raw, print warning and continue
            if not raw:
                print("[WARN] LLM returned nothing. Trying again...")
                continue

            # Sanitize
            last_raw = raw.strip()

            # Use our extractor to pull out a real SQL query from messy text
            cleaned_sql = SqlLiteUtil.parse_sql_string(last_raw)

            # If the cleaning worked, done
            if cleaned_sql:
                obj.llm_returned_sql = cleaned_sql

                # Return
                return cleaned_sql

            print("[WARN] Bad SQL from LLM. Trying again...")

            # Temporarily sleep to for LLM API rate limit 
            time.sleep(0.4)

        # If all retries fail, return an error message
        fail_msg = f"-- ERROR: invalid SQL generated\n-- Last output:\n{last_raw}"
        obj.llm_returned_sql = fail_msg
        
        # Return
        return fail_msg

    @staticmethod
    def generate_sql_for_objs(
        obj_list,
        api_key,
    ):
        # Wrapper function to call on list of objects 
        #
        # Generate LLM SQL for a list of DatasetTestObj objects sequentially.

        # Init where store results
        results = []
        
        # Loop through each object, generate SQL for each
        counter = 1
        for obj in obj_list:
            
            # Call
            try:
                results.append(SqlLiteUtil.generate_sql_for_obj(obj, api_key))
                print(f"Completed SQL generation for {counter} out of {len(obj_list)} items.\n\n")
                counter += 1

            # Catch and print errors
            except Exception as e:
                print(f"[ERROR] SQL generation failed: {e}")

        # Return results
        return results

    @staticmethod
    def parse_sql_string(raw):
        # Extract a clean SQL query from inconsistent LLM output
        
        # If raw is not a string, return None
        if not isinstance(raw, str):
            return None

        # Remove leading/trailing characters; return that value            
        text = raw.strip()
        
        # Remove common llm noise
        text = re.sub(r"^(sql:|sql|query:)\s*", "", text, flags=re.IGNORECASE).strip()

        # Locate the start of a real SQL statement using keywords
        sql_start = re.search(
            r"\b(SELECT|WITH|INSERT|UPDATE|DELETE)\b",
            text,
            flags=re.IGNORECASE
        )

        # If no sql start found, return None
        if not sql_start:
            return None

        # More string processing    
        text = text[sql_start.start():].strip()

        # Remove leftover ``` characters from LLM output if exists
        text = text.rstrip("`").strip()

        # Remove trailing inline comments if exists
        text = re.split(r"(--|#)", text)[0].strip()

        # Return "lean final SQL text"
        return text if text else None 
