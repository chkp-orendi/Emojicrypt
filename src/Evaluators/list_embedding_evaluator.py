import os
import sys

from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import get_embedding, cosine_similarity

class ListEmbeddingEvaluator(EvaluatorTemplate):

    @staticmethod
    def _find_leftovers(obfuscated_prompt, terms):
        count = 0
        for term in terms:
            if term in obfuscated_prompt:
                count += 1
        return count/len(terms)

    @staticmethod
    def evaluate_prompt(obfuscated_prompt, case_data):
        obfuscated_prompt_embeddings = get_embedding(obfuscated_prompt)
        cosine_similarity = cosine_similarity(obfuscated_prompt_embeddings, case_data["original_embeddings"])
        list_leftovers = ListEmbeddingEvaluator._find_leftovers(obfuscated_prompt, case_data["list"])
        return {"similarity": cosine_similarity, "leftovers": list_leftovers}

    @staticmethod
    def evaluate_answer(obfuscated_answer, case_data):
        obfuscated_answer_embeddings = get_embedding(obfuscated_answer)
        return cosine_similarity(obfuscated_answer_embeddings, case_data["original_answer_embeddings"])
