import random
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List


def deterministic_random_sample(data_list, seed, length):

    # Randomly choose 'length' amount of objects from data_list
    #
    # It is random but deterministic based on the seed
    #
    # Using SHA-256, we can create a deterministic number from the seed string
    #
    # Use this number to create a Python Random object then sample() get our
    #   list of objects deterministically, all the time

    if length > len(data_list):
        raise ValueError("length cannot be greater than size of data_list")

    seed_bytes = seed.encode('utf-8')
    hash_digest = hashlib.sha256(seed_bytes).hexdigest()
    int_seed = int(hash_digest, 16)

    rnd = random.Random(int_seed)
    return rnd.sample(data_list, length)


@dataclass
class DatasetTestObj:
    # Set on init
    sort_id: int = 0            # debugging; also the item location within dev.json per dataset
    dev_db_id: str = ""
    dev_db_path: str = ""
    dev_question: str = ""
    dev_gold_sql: str = ""
    dev_gold_sql_output: str = ""

    # Set before calling LLM
    rag_examples: List[Any] = field(default_factory=list)           # Python interpreter requires type definition
    schema_string = ""
    schema_linking_tables: List[Any] = field(default_factory=list)  # Python interpreter requires type definition
    
    # LLM data and response
    llm_prompt: str = ""
    llm_returned_sql: str = ""
    llm_sql_output: str = ""
    
    # Metrics for
    em: float = 0.0
    ex: float = 0.0
    partial_correctness: float = 0.0
