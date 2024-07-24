import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libraries')))
from AzureApi import get_embedding, cosine_similarity

class EmbeddingEvaluator:
    @staticmethod
    def evaluate_prompt(obfuscated_prompt, case_data):
        obfuscated_prompt_embeddings = get_embedding(obfuscated_prompt)
        return cosine_similarity(obfuscated_prompt_embeddings, case_data["original_embeddings"])

    @staticmethod
    def evaluate_answer(obfuscated_answer, case_data):
        obfuscated_answer_embeddings = get_embedding(obfuscated_answer)
        return cosine_similarity(obfuscated_answer_embeddings, case_data["original_answer_embeddings"])
