import os
import sys
import json
from datetime import datetime
import logging

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
        case_data["used_dictionary"] = self._obf.get_dictionary()
        case_data["obfuscated_answer"] = obfuscated_answer

        prompt_metric_reasoning, prompt_metric, guess_results = self._evaluator.evaluate_prompt(obfuscated_prompt, case_data)
        answer_metric_reasoning, answer_metric = self._evaluator.evaluate_answer(deobfuscated_answer, case_data)
        obfuscated_dictonary = self._obf.get_dictionary()
        eval_time = datetime.now() - time
        eval_results = {
            "original_prompt": case_data["original_prompt"],
            "obfuscated_prompt": obfuscated_prompt, "obfuscated_answer":obfuscated_answer,
            "deobfuscated_answer": deobfuscated_answer, "original_answer": case_data["original_answer"],
            "prompt_metric": prompt_metric, "answer_metric": answer_metric,
            "prompt_metric reasoning": prompt_metric_reasoning, "answer_metric reasoning": answer_metric_reasoning,
            "obfuscated_dictonary": obfuscated_dictonary,
            "evaluation time": str(eval_time)
        }
        if guess_results["number_of_emoji_in_prompt"]!=0:
            eval_results["prompt_metric"]["guessed_correct"] = guess_results["guessed_correct"]/guess_results["number_of_emoji_in_prompt"]
        eval_results.update(guess_results)
        self.logger.info(eval_results)

        return  eval_results

def evaluate_batch(data_set, obfuscator, evaluator_factory):
    #use pandas frame?
    metrics = []
    logger = logging.getLogger("__main__")
    evaluator = SingleCaseEvaluator(obfuscator,logger, evaluator_factory)
    i =0
    for case in data_set:
        print(i)
        # logger.info(f"case {i}")
        i += 1
        metrics.append(evaluator.evaluate(case))

        output_folder_path = os.path.join(os.getenv("PROJECT_PATH"),"data", "September-2024", os.getenv("DATE"))
        json.dump(metrics, open(os.path.join(output_folder_path,"checkpoint.json"), "w", encoding = 'utf-8'), ensure_ascii= False , indent=4)
    return metrics