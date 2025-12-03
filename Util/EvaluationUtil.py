from typing import List, Tuple
from collections import Counter


class EvaluationUtil:

    @staticmethod
    def _normalize_sql(sql):
        # Check if sql
        if not sql:
            return ""

        # Sanitize
        cleaned = sql.strip().rstrip(";")
        cleaned = " ".join(cleaned.split())

        # Return
        return cleaned.lower()

    @staticmethod
    def compute_em(gold_sql, predicted_sql):

        # EM = Exact Match
        #
        # Arguably the strictest check
        # 
        # It only passes if the SQL query string matches exactly
        #
        # Useful to see when the model reproduces the actual expected query

        # Normalize first
        g = EvaluationUtil._normalize_sql(gold_sql)
        p = EvaluationUtil._normalize_sql(predicted_sql)
        
        # Return 1.0 if they match, otherwise 0.0
        return 1.0 if g == p else 0.0

    @staticmethod
    def compute_ex(gold_result, pred_result):

        # EX = Execution Accuracy
        #
        # This checks whether the two result sets contain the same rows.
        #   Order doesn't matter, since SQL doesn't really guarentee this unless
        #   using ORDER BY clause
        #
        # This metric tells us if the model solved the question,
        #   regardless of how the SQL is written.

        # Check for none
        if gold_result is None or pred_result is None:
            return 0.0

        # Use a Python Counter object to compare the two result sets
        #
        # If they are the same, return 1.0, otherwise 0.0
        return 1.0 if Counter(gold_result) == Counter(pred_result) else 0.0

    @staticmethod
    def _flatten_row(row: Tuple) -> List:
        # Rows come back as tuples at arrival we just expand them into a list
        #   so it's easier to compare individual values

        return list(row)

    @staticmethod
    def _extract_values(result):
        # Pull out every numerical values returned by the query
        #
        # The 'partial_correctness' metric used later is based on comparing these sets of values.

        # Check for none
        if result is None:
            return set()

        # Init values list
        values = []

        # Loop through each row, flatten and add to values list
        for row in result:
            values.extend(EvaluationUtil._flatten_row(row))

        # Return
        return set(values)


    @staticmethod
    def compute_partial_correctness(gold_result, pred_result):

        # partial_correctness (self-defined metric) = evaluates for partial correctness
        #
        # Intuition:
        # 
        # Sometimes a model's SQL is wrong, but it still retrieves some correct
        #   pieces of information. This score hopes to measure how much of the correct
        #   data my model managed to recover.
        #
        # The idea is simple: look at which values show up in both the dev gold
        #   results and the llm predicted results, then compute how much of the gold output
        #   set was recovered.

        # Extract values from gold and predicted results
        gold_vals = EvaluationUtil._extract_values(gold_result)
        pred_vals = EvaluationUtil._extract_values(pred_result)

        # Check for none
        if not gold_vals:
            return 0.0

        # Get intersection of gold and predicted values
        hits = gold_vals.intersection(pred_vals)

        # Return
        return len(hits) / len(gold_vals)


    @staticmethod
    def evaluate_all(obj):
        # All Tests
        
        # Run them all; get them all
        return {
            "em": EvaluationUtil.compute_em(obj.dev_gold_sql, obj.llm_returned_sql),
            "ex": EvaluationUtil.compute_ex(obj.dev_gold_sql_output, obj.llm_sql_output),
            "partial_correctness": EvaluationUtil.compute_partial_correctness(obj.dev_gold_sql_output, obj.llm_sql_output),
        }
    
    @staticmethod
    def print_avg_metrics(list_of_objs):
        # Print average metrics for a list of objects

        # Init sums
        em_sum = 0
        ex_sum = 0
        partial_correctness_sum = 0

        # Loop through each object, add to sums
        for obj in list_of_objs:
            em_sum += obj.em
            ex_sum += obj.ex
            partial_correctness_sum += obj.partial_correctness

        # Calculate averages
        avg_em = em_sum / len(list_of_objs)
        avg_ex = ex_sum / len(list_of_objs)
        avg_partial_correctness = partial_correctness_sum / len(list_of_objs)

        # Print averages
        print(f"\n\n\n-----MEAN METRICS-----\n\n\nAverage EM: {avg_em}")
        print(f"Average EX: {avg_ex}")
        print(f"Average partial_correctness: {avg_partial_correctness}")
