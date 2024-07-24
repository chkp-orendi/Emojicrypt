import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libraries')))
import AzureApi

class ListEmbeddingEvaluator:

    @staticmethod
    def _find_leftovers(obfuscated_prompt, terms):
        count = 0
        for term in terms:
            if term in obfuscated_prompt:
                count += 1
        return count/len(terms)

    @staticmethod
    def evaluate_prompt(obfuscated_prompt, case_data):
        obfuscated_prompt_embeddings = AzureApi.get_embedding(obfuscated_prompt)
        cosine_similarity = AzureApi.cosine_similarity(obfuscated_prompt_embeddings, case_data["original_embeddings"])
        list_leftovers = ListEmbeddingEvaluator._find_leftovers(obfuscated_prompt, case_data["list"])
        return (cosine_similarity, list_leftovers)

    @staticmethod
    def evaluate_answer(obfuscated_answer, case_data):
        obfuscated_answer_embeddings = AzureApi.get_embedding(obfuscated_answer)
        return AzureApi.cosine_similarity(obfuscated_answer_embeddings, case_data["original_answer_embeddings"])
