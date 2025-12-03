import json
import os
from typing import List

from Model.DatasetTestObj import DatasetTestObj

class LoadDevJson:

    @staticmethod
    def load_bird_dev_json():
        # Load all items from dev.json into a list of DatasetTestObj objects

        # Check if file exists
        if not os.path.exists("Dataset/bird/dev.json"):
            raise FileNotFoundError(f"Could not find file at Dataset/bird/dev.json")

        # Open file and load json
        with open("Dataset/bird/dev.json", "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        dataset_objects: List[DatasetTestObj] = []

        counter = 0
        # Load
        for item in raw_items:

            obj = DatasetTestObj(
                sort_id=counter,
                dev_db_id=item.get("db_id", ""),
                dev_db_path=item.get("db_path", ""),
                dev_question=item.get("question", ""),
                dev_gold_sql=item.get("SQL", ""),
                llm_sql_output="",
                dev_gold_sql_output=""
            )

            dataset_objects.append(obj)
            counter += 1

        return dataset_objects

    @staticmethod
    def load_spider_dev_json():
        # Load all items from dev.json into a list of DatasetTestObj objects
        dev_path = "Dataset/spider-1.0/dev.json"

        # Ensure file exists
        if not os.path.exists(dev_path):
            raise FileNotFoundError(f"Could not find file at {dev_path}")

        # Load json
        with open(dev_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        # Create list of DatasetTestObj objects
        dataset_objects = []

        # Load each item into a DatasetTestObj object
        counter = 0
        for item in raw_items:

            obj = DatasetTestObj(
                sort_id=counter,
                dev_db_id=item.get("db_id", ""),
                dev_db_path="",
                dev_question=item.get("question", ""),
                dev_gold_sql=item.get("query", ""),
                llm_sql_output="",
                dev_gold_sql_output=""
            )

            dataset_objects.append(obj)
            counter += 1

        return dataset_objects

