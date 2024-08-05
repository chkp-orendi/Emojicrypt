import os
import sys

from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import get_embedding, cosine_similarity



class EmbeddingEvaluator(EvaluatorTemplate):
    @staticmethod
    def evaluate_prompt(obfuscated_prompt, case_data):
        obfuscated_prompt_embeddings = get_embedding(obfuscated_prompt)
        return cosine_similarity(obfuscated_prompt_embeddings, case_data["original_embeddings"])

    @staticmethod
    def evaluate_answer(obfuscated_answer, case_data):
        obfuscated_answer_embeddings = get_embedding(obfuscated_answer)
        return cosine_similarity(obfuscated_answer_embeddings, case_data["original_answer_embeddings"])
