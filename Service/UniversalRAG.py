import json
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class UniversalRAG:
    

    # My main endgoal is RAG or Retrieval Augmented Generation
    # 
    # I use TF-IDF and cosine similarity because it lets me compare how close two questions are.
    #
    # These tools then turn text into vectors the computer understands so we can rank which training questions
    #   are most related to a user’s input.
    #
    # This is consistent with the paper approach that this project topic is based on
    #
    # I also noticed a lot of performance bottlenecks running this for EVERY question cheaply; more speed
    #   and parallel/concurrent execution is costly machine-wise/financially
    #
    # Init this object once, more expensive once, then SUPER fast compute calls per question
    #
    # This is also adaptable to whether you are using BIRD or Spider 1.0 datasets; no excessive code waste


    def __init__(self, dataset_root: str, dataset_name: str):
        # Directory containing the passed dataset's json files
        self.dataset_root = dataset_root
        
        # The dataset you are using
        self.dataset_name = dataset_name.lower().strip()

        # We store all training items here
        self.train_items = []

        # Store question text for indexing, which allows for better performance optimzation
        self.train_questions = []

        # Schema information per database
        self.schemas = {}

        # TF-IDF model and question matrix we will use in our implementation
        self.vectorizer = None
        self.question_vectors = None

        # Flag to check if index + schema have been built
        self.ready = False

    # Load all the training data; we will run RAG on the training set to retrieve 
    #   perceived optimal/similar example questions
    def load_train(self):
        
        # Either load Bird or Spider 1.0 training data
        if self.dataset_name == "bird":
            path = os.path.join(self.dataset_root, "train.json")
            with open(path, "r") as f:
                self.train_items = json.load(f)

        elif self.dataset_name == "spider-1.0":
            spider_files = ["train_spider.json", "train_others.json"]
            combined = []

            # Builds a full file path for each JSON file inside the dataset folder.
            for filename in spider_files:
                path = os.path.join(self.dataset_root, filename)
                if os.path.exists(path):
                    with open(path, "r") as f:
                        combined.extend(json.load(f))

            # Standardize the field names to match the format
            self.train_items = []
            for item in combined:
                self.train_items.append({
                    "question": item["question"],
                    "SQL": item["query"],
                    "db_id": item["db_id"],
                })
        else:
            # Wrong string or a dataset not supported for this project
            raise ValueError(f"Unsupported dataset: {self.dataset_name}")

        # Store only questions for vector index
        self.train_questions = [item["question"] for item in self.train_items]

    # Load table and column names for all databases
    def load_rag_schema(self):
        
        # Correctly grab filename and path for execution per dataset
        filename = "train_tables.json" if self.dataset_name == "bird" else "tables.json"
        path = os.path.join(self.dataset_root, filename)

        # Open the file and load json
        with open(path, "r") as f:
            raw = json.load(f)

        # BIRD and Spider 1.0 jsons are not uniform; need to process accordingly
        for entry in raw:
            db_id = entry["db_id"]

            table_names = {name.lower() for name in entry["table_names_original"]}
            col_names = {col[1].lower() for col in entry["column_names_original"]}

            self.schemas[db_id] = {
                "tables": table_names,
                "columns": col_names,
            }
            
    # Build the semantic index using TF-IDF
    def build_index(self):
        print("Building TF-IDF index...")

        # Each training question is converted into a TF-IDF vector
        #
        # TF-IDF effectively highlights the important words in a string and downplays common ones
        #
        # With everything in vector form, we can compare questions numerically to find the closest matches

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.question_vectors = self.vectorizer.fit_transform(self.train_questions)

        print(f"Indexed {len(self.train_questions)} questions.")

    # Function to init everything; only needs to be called once
    def initialize(self):
        # double check readiness
        if self.ready:
            return

        # Load data, schema, and build index
        self.load_train()
        self.load_rag_schema()
        self.build_index()

        self.ready = True

    # Compute simple schema relevance for the question’s DB
    def rag_schema_score(self, question, db_id):
        
        # Must use a valid schema available
        if db_id not in self.schemas:
            return 0.0

        # Simple matching: count how many column and table names appear in the question
        words = {w.lower() for w in question.split()}
        schema = self.schemas[db_id]

        # Find matches
        col_match = words.intersection(schema["columns"])
        table_match = words.intersection(schema["tables"])

        # Columns usually provide the strongest clue, so it can be a good idea to weigh them more
        return len(col_match) + 0.5 * len(table_match)

    # Our main entry point; this is the function that effectively 'runs' everything
    def retrieve(self, question, k):
        
        # Entry point can't run on a object that hasn't been initialized
        if not self.ready:
            raise RuntimeError("UniversalRAG must be initialized before running retrieve().")

        # Convert our passed question into TF-IDF vector; benefits of this listed earlier; can elaborate
        #   much more if needed
        vector = self.vectorizer.transform([question])

        # Compute semantic similarity between passed question and all training questions
        semantic_scores = cosine_similarity(vector, self.question_vectors).flatten()

        # List to store final ranking of training items
        ranking = []
        
        # Loop
        for i, sem in enumerate(semantic_scores):

            # For each training item, get item and its DB ID
            item = self.train_items[i]
            db_id = item["db_id"]

            # Compute final score for the question's DB then add
            schema_rel = self.rag_schema_score(question, db_id)
            final_score = float(sem) + 0.1 * schema_rel
            ranking.append((final_score, i))

        # Sort by final score descending and grab top k
        ranking.sort(key=lambda x: x[0], reverse=True)
        top = ranking[:k]

        # Build results
        results = []
        
        # Loop
        for score, index in top:
            
            # Grab the training item
            item = self.train_items[index]

            # Store only relevant fields in the results
            results.append({
                "question": item["question"],       # !IMPORTANT
                "sql": item["SQL"],                 # !IMPORTANT
                "db_id": item["db_id"],             # !IMPORTANT
                "final_score": round(score, 4),     # !IMPORTANT
            })

        # Return
        return results

    def run_rag(self, question, k):
        
        # Get RAG per question and number, k, of examples you want
        return self.retrieve(question, k)
