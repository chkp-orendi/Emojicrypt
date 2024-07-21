import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../libraries'))
import AzureApi
class SingleCaseEvaluator:
    def __init__(self, obfuscator):
        self._obf = obfuscator

    def evaluate(self, case_data):
        obfuscated_prompt = self._obf.obfuscate(case_data["original_prompt"])
        obfuscated_prompt_embeddings = AzureApi.get_embedding(obfuscated_prompt)
        obfuscated_answer = AzureApi.get_answer(obfuscated_prompt, "gpt-4")
        obfuscated_answer_embeddings = AzureApi.get_embedding(obfuscated_answer)

        prompt_metric = AzureApi.cosine_similarity(obfuscated_prompt_embeddings, case_data["original_embeddings"])
        answer_metric = AzureApi.cosine_similarity(obfuscated_answer_embeddings, case_data["original_answer_embeddings"])

        return prompt_metric, answer_metric, obfuscated_answer

def evaluate_batch(data_set, obfuscator):
    #use pandas frame?
    metrics = []
    evaluator = SingleCaseEvaluator(obfuscator)
    for case in data_set:
        metrics.append(evaluator.evaluate(case))
    return metrics
