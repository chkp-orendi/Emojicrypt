import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../libraries'))
import AzureApi

class EmbeddingEvaluator:
    @staticmethod
    def evaluate_prompt(obfuscated_prompt, case_data):
        obfuscated_prompt_embeddings = AzureApi.get_embedding(obfuscated_prompt)
        return AzureApi.cosine_similarity(obfuscated_prompt_embeddings, case_data["original_embeddings"])

    @staticmethod
    def evaluate_answer(obfuscated_answer, case_data):
        obfuscated_answer_embeddings = AzureApi.get_embedding(obfuscated_answer)
        return AzureApi.cosine_similarity(obfuscated_answer_embeddings, case_data["original_answer_embeddings"])
