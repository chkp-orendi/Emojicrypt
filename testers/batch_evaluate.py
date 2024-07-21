import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../libraries'))
import AzureApi
class SingleCaseEvaluator:
    def __init__(self, obfuscator, logger):
        self._obf = obfuscator
        self.logger = logger

    def _evaluate_prompt(self, obfuscated_prompt, case_data):
        obfuscated_prompt_embeddings = AzureApi.get_embedding(obfuscated_prompt)
        return AzureApi.cosine_similarity(obfuscated_prompt_embeddings, case_data["original_embeddings"])

    def _evaluate_answer(self, obfuscated_answer, case_data):
        obfuscated_answer_embeddings = AzureApi.get_embedding(obfuscated_answer)
        return AzureApi.cosine_similarity(obfuscated_answer_embeddings, case_data["original_answer_embeddings"])

    def evaluate(self, case_data):
        obfuscated_prompt = self._obf.obfuscate(case_data["original_prompt"])
        obfuscated_answer = AzureApi.get_answer(obfuscated_prompt, "gpt-4")
        deobfuscated_answer = self._obf.deobfuscate(obfuscated_answer)
        prompt_metric = self._evaluate_prompt(obfuscated_prompt, case_data)
        answer_metric = self._evaluate_answer(deobfuscated_answer, case_data)
        self.logger.info(f"""
obfuscated prompt: {obfuscated_prompt}
obfuscated answer: {obfuscated_answer}
deobfuscated_answer: {deobfuscated_answer}
prompt_metric: {prompt_metric}
answer_metric: {answer_metric}""")
        
        return prompt_metric, answer_metric, obfuscated_answer

def evaluate_batch(data_set, obfuscator,logger):
    #use pandas frame?
    metrics = []
    evaluator = SingleCaseEvaluator(obfuscator,logger)
    for case in data_set:
        metrics.append(evaluator.evaluate(case))
    return metrics
