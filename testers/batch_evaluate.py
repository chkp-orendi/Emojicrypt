import os
import sys
from embedding_evaluator import EmbeddingEvaluator
from list_embedding_evaluator import ListEmbeddingEvaluator
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libraries')))
import AzureApi

class SingleCaseEvaluator:
    def __init__(self, obfuscator, logger, evaluator):
        self._obf = obfuscator()
        self.logger = logger
        self._evaluator = evaluator

    def evaluate(self, case_data):
        time = datetime.now()
        obfuscated_prompt = self._obf.obfuscate(case_data["scenario"])
        obfuscated_answer = AzureApi.get_answer(obfuscated_prompt)
        deobfuscated_answer = self._obf.deobfuscate(obfuscated_answer)
        prompt_metric = self._evaluator.evaluate_prompt(obfuscated_prompt, case_data=case_data)
        answer_metric = self._evaluator.evaluate_answer(deobfuscated_answer, case_data=case_data)
        obfuscated_dictonary = self._obf.get_dictionary()
        eval_time = datetime.now() - time
        self.logger.info(f"""
obfuscated prompt: {obfuscated_prompt}
obfuscated answer: {obfuscated_answer}
deobfuscated_answer: {deobfuscated_answer}
prompt_metric: {prompt_metric}
answer_metric: {answer_metric}
obfuscated_dictonary: {obfuscated_dictonary}
"evaluation time": {eval_time}""")
        print(f"""
obfuscated prompt: {obfuscated_prompt}
obfuscated answer: {obfuscated_answer}
deobfuscated_answer: {deobfuscated_answer}
prompt_metric: {prompt_metric}
answer_metric: {answer_metric}
obfuscated_dictonary: {obfuscated_dictonary}
evaluation time: {eval_time}""")
        return  {
            "original_answer": case_data["original_answer"], "original_prompt": case_data["scenario"],
            "obfuscated_prompt": obfuscated_prompt, "obfuscated_answer":obfuscated_answer,
            "deobfuscated_answer": deobfuscated_answer,
            "prompt_metric": prompt_metric, "answer_metric": answer_metric,
            "obfuscated_dictonary": obfuscated_dictonary,
            "evaluation time": str(eval_time)
        }

def evaluate_batch(data_set, obfuscator,logger):
    #use pandas frame?
    metrics = []
    evaluator = SingleCaseEvaluator(obfuscator,logger, ListEmbeddingEvaluator)
    i =0
    for case in data_set:
        print(i)
        logger.info(f"case {i}")
        i += 1
        metrics.append(evaluator.evaluate(case))
    return metrics
