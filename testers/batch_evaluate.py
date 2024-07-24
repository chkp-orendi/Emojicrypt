import os
import sys
from embedding_evaluator import EmbeddingEvaluator
from list_embedding_evaluator import ListEmbeddingEvaluator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libraries')))
import AzureApi

class SingleCaseEvaluator:
    def __init__(self, obfuscator, logger, evaluator):
        self._obf = obfuscator()
        self.logger = logger
        self._evaluator = evaluator

    def evaluate(self, case_data):
        obfuscated_prompt = self._obf.obfuscate(case_data["scenario"])
        obfuscated_answer = AzureApi.get_answer(obfuscated_prompt)
        deobfuscated_answer = self._obf.deobfuscate(obfuscated_answer)
        prompt_metric = self._evaluator.evaluate_prompt(obfuscated_prompt, case_data=case_data)
        answer_metric = self._evaluator.evaluate_answer(deobfuscated_answer, case_data=case_data)
        obfuscated_dictonary = self._obf.get_dictionary()
        self.logger.info(f"""
obfuscated prompt: {obfuscated_prompt}
obfuscated answer: {obfuscated_answer}
deobfuscated_answer: {deobfuscated_answer}
prompt_metric: {prompt_metric}
answer_metric: {answer_metric}
obfuscated_dictonary: {obfuscated_dictonary}""")
        print(f"""
obfuscated prompt: {obfuscated_prompt}
obfuscated answer: {obfuscated_answer}
deobfuscated_answer: {deobfuscated_answer}
prompt_metric: {prompt_metric}
answer_metric: {answer_metric}
obfuscated_dictonary: {obfuscated_dictonary}""")
        
        return  {
            "original_answer": case_data["original_answer"], "original_prompt": case_data["scenario"],
            "obfuscated_prompt": obfuscated_prompt, "obfuscated_answer":obfuscated_answer,
            "deobfuscated_answer": deobfuscated_answer,
            "prompt_metric": prompt_metric, "answer_metric": answer_metric,
            "obfuscated_dictonary": obfuscated_dictonary
        }

def evaluate_batch(data_set, obfuscator,logger):
    #use pandas frame?
    metrics = []
    evaluator = SingleCaseEvaluator(obfuscator,logger, ListEmbeddingEvaluator)
    i =0
    for case in data_set:
        print(i)
        i += 1
        metrics.append(evaluator.evaluate(case))
    return metrics
