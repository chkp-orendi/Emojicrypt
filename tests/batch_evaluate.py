import os
import sys
from datetime import datetime


from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH")) # type: ignore[arg-type]
from src.utils.azure_client import get_answer

class SingleCaseEvaluator:
    def __init__(self, obfuscator, logger, evaluator_factory):
        self._obf = obfuscator()
        self.logger = logger
        self._evaluator = evaluator_factory()       ## create evaluator, maybe in future evaluator will have some input parameters

    def evaluate(self, case_data):
        time = datetime.now()
        obfuscated_prompt = self._obf.obfuscate(case_data)
        obfuscated_answer = get_answer(obfuscated_prompt)
        deobfuscated_answer = self._obf.deobfuscate(obfuscated_answer)
        prompt_metric_reasoning, prompt_metric = self._evaluator.evaluate_prompt(obfuscated_prompt, case_data)
        answer_metric_reasoning, answer_metric = self._evaluator.evaluate_answer(deobfuscated_answer, case_data)
        obfuscated_dictonary = self._obf.get_dictionary()
        eval_time = datetime.now() - time
        self.logger.info(f"""
obfuscated prompt: {obfuscated_prompt}
obfuscated answer: {obfuscated_answer}
deobfuscated_answer: {deobfuscated_answer}
prompt_metric: {prompt_metric}
prompt_metric reasoning: {prompt_metric_reasoning}
answer_metric: {answer_metric}
answer_metric reasoning: {answer_metric_reasoning}
obfuscated_dictonary: {obfuscated_dictonary}
evaluation time: {eval_time}""")
#         print(f"""
# obfuscated prompt: {obfuscated_prompt}
# obfuscated answer: {obfuscated_answer}
# deobfuscated_answer: {deobfuscated_answer}
# prompt_metric: {prompt_metric}
# answer_metric: {answer_metric}
# obfuscated_dictonary: {obfuscated_dictonary}
# evaluation time: {eval_time}""")
        return  {
            "original_answer": case_data["original_answer"], "original_prompt": case_data["original_question"],
            "obfuscated_prompt": obfuscated_prompt, "obfuscated_answer":obfuscated_answer,
            "deobfuscated_answer": deobfuscated_answer,
            "prompt_metric": prompt_metric, "answer_metric": answer_metric,
            "prompt_metric reasoning": prompt_metric_reasoning, "answer_metric reasoning": answer_metric_reasoning,
            "obfuscated_dictonary": obfuscated_dictonary,
            "evaluation time": str(eval_time)
        }

def evaluate_batch(data_set, obfuscator,logger, evaluator_factory):
    #use pandas frame?
    metrics = []
    evaluator = SingleCaseEvaluator(obfuscator,logger, evaluator_factory)
    i =0
    for case in data_set:
        print(i)
        logger.info(f"case {i}")
        i += 1
        metrics.append(evaluator.evaluate(case))
    return metrics