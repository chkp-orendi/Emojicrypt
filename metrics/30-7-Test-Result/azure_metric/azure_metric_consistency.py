import os
import sys
import glob
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Evaluators')))
from gpt_evaluator import GPTEvaluator


prompt_file_name = "emphasis_on_technical_terms.txt"
path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "prompts", "gpt_evaluator" ,prompt_file_name)
evaluator = GPTEvaluator(path)


data_path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "metrics", "30-7-Test-Result", "azure_metric")
llama__prefix_file = os.path.join(data_path, "2024-07-30_14_14_47.797507-metrics-llama-prefix.json")
gpt_prefix_file = os.path.join(data_path, "2024-07-30_14_41_24.191617-metrics-gpt-prefix.json")

with open(llama__prefix_file, 'r') as f:
    data = json.load(f)

for obfuscator in data:
    print( obfuscator[0] )
    if obfuscator[0] == "ThreePromptsObfuscator - Llama3:8b":
        avrage = 0
        llama_prefix_data = obfuscator[1]
        for result_dict in llama_prefix_data[:10]:
            eval_answer = evaluator.evaluate_prompt(result_dict['obfuscated_prompt'], {"scenario": result_dict["original_prompt"]})
            print (f"eval_answer: {eval_answer}")
            avrage += eval_answer
        print (f"final avrage = {avrage/10}")