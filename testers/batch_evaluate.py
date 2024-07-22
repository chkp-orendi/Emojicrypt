import os
import sys
from embedding_evaluator import EmbeddingEvaluator
sys.path.append(os.path.join(os.path.dirname(__file__), '../libraries'))
import AzureApi
class SingleCaseEvaluator:
    def __init__(self, obfuscator, logger, evaluator):
        self._obf = obfuscator
        self.logger = logger
        self._evaluator = evaluator

    def evaluate(self, case_data):
        obfuscated_prompt = self._obf.obfuscate(case_data["scenario"])
        obfuscated_answer = AzureApi.get_answer(obfuscated_prompt, "gpt-4")
        deobfuscated_answer = self._obf.deobfuscate(obfuscated_answer)
        prompt_metric = self._evaluator.evaluate_prompt(obfuscated_prompt, case_data=case_data)
        answer_metric = self._evaluator.evaluate_answer(deobfuscated_answer, case_data=case_data)
        self.logger.info(f"""
obfuscated prompt: {obfuscated_prompt}
obfuscated answer: {obfuscated_answer}
deobfuscated_answer: {deobfuscated_answer}
prompt_metric: {prompt_metric}
answer_metric: {answer_metric}""")
        
        return prompt_metric, answer_metric, deobfuscated_answer

def evaluate_batch(data_set, obfuscator,logger):
    #use pandas frame?
    metrics = []
    evaluator = SingleCaseEvaluator(obfuscator,logger, EmbeddingEvaluator)
    for case in data_set:
        metrics.append(evaluator.evaluate(case))
    return metrics
