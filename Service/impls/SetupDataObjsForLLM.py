import json
import os
from typing import List
from typing import List, Callable, Any
from Util.SchemaUtil import SchemaUtil


class SetupDataObjsForLLM:
    
    
    @staticmethod
    def setup_data_objs_for_llm(
        data_list,
        LLM_API_KEY,
        rag_instance,
        db_map,
        extract_schema_fn,
        schema_linking_fn,
        top_k
    ):
        def process_item(obj):
            
            print(f"Processing item {obj.sort_id} - DB ID: {obj.dev_db_id}")

            # Normalize path
            obj.dev_db_path = obj.dev_db_path if obj.dev_db_path.startswith("Dataset") \
                else "Dataset/bird/dev_databases/" + obj.dev_db_path

            # RAG
            obj.rag_examples = rag_instance.run_rag(obj.dev_question, top_k)

            # Schema extraction
            obj.schema_string = extract_schema_fn(db_map[obj.dev_db_id])

            # Schema linking (LLM)
            obj.schema_linking_tables = schema_linking_fn(LLM_API_KEY, obj.schema_string, obj.dev_question)

            return obj

        # Sequential execution
        counter = 1
        for item in data_list:
            process_item(item)
            print(f"Completed {counter} out of {len(data_list)} items.\n\n")
            counter += 1
        return data_list