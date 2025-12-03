from Service.impls.GetRag import GetRag
from Service.impls.LoadDevJson import LoadDevJson
from Service.impls.SetupDataObjsForLLM import SetupDataObjsForLLM
from Model.DatasetTestObj import deterministic_random_sample

from Util.CommonUtil import CommonUtil
from Util.SchemaUtil import SchemaUtil
from Util.SqlLiteUtil import SqlLiteUtil
from Util.EvaluationUtil import EvaluationUtil

import time

class BirdService:

    @staticmethod
    def test_algo_on_bird_dataset(LLM_API_KEY, NUM_ITEMS_TO_TEST, SEED):

        # Hashmap where key is db_id and value is db_path
        bird_db_map = SqlLiteUtil.load_sqlite_databases("bird", base_path="Dataset")
        
        # Get the one RAG instance that will be ran for all items
        rag = GetRag.get_bird_rag()
        
        # Load all items from dev.json into a list of DatasetTestObj objects
        data_list = LoadDevJson.load_bird_dev_json()

        # Deterministically select NUM_ITEMS_TO_TEST items using a SEED string
        sampled_list = deterministic_random_sample(data_list, SEED, NUM_ITEMS_TO_TEST)
        
        # Init certain fields within each item for their llm call
        updated_list = SetupDataObjsForLLM.setup_data_objs_for_llm(
            sampled_list,
            LLM_API_KEY,
            rag,
            bird_db_map,
            SchemaUtil.extract_schema_from_sqlite,
            SchemaUtil.schema_linking,
            5
        )
        print(f"---------- Sleep 5 seconds to let llm API rate limit cool down\n\n")
        time.sleep(5)

        # Make sure necessary fields set before proceeding
        for obj in updated_list:
            fields_set_flag = CommonUtil.verify_dataset_test_obj_fields(obj)

            if not fields_set_flag:
                print(f"[ERROR] Item {obj.sort_id} - DB ID: {obj.dev_db_id} - Fields not set\n\nProcessing stopped...")
                return

        # Generate LLM SQL for each object
        SqlLiteUtil.generate_sql_for_objs(updated_list, LLM_API_KEY)

        
        print(f"Completed processing {len(updated_list)} items sequentially.\n\n\n\n")
        for obj in updated_list:

            # Run SQL queries
            obj.llm_sql_output = SqlLiteUtil.run_sql_query(obj.llm_returned_sql, bird_db_map[obj.dev_db_id])
            obj.dev_gold_sql_output = SqlLiteUtil.run_sql_query(obj.dev_gold_sql, bird_db_map[obj.dev_db_id])

            eval_obj = EvaluationUtil.evaluate_all(obj)
            obj.em = eval_obj["em"]
            obj.ex = eval_obj["ex"]
            obj.partial_correctness = eval_obj["partial_correctness"]
        

        EvaluationUtil.print_avg_metrics(updated_list)
        
        

        print(f"\n\n\n\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$Completed processing {len(updated_list)} items sequentially.")


        
        