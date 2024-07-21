from batch_evaluate import evaluate_batch
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../libraries'))
#TODO: proper module structure
from ThreePromptObfuscator import ThreePromptsObfuscator
from fake_obfuscator import FakeObfuscator
from wrong_obfuscator import WrongObfuscator
from ollama_helper import OllamaHelper

sensitive_file_path = "prompts/sensitive_prompt.txt"
crucial_file_path = "prompts/crucial_prompt.txt"
replace_file_path = "prompts/replace_prompt.txt"

def evaluate_with_obfuscators(data, obfuscators):
    metrics = []
    for obfuscator in obfuscators:
        metrics.append(evaluate_batch(data, obfuscator))
    return metrics

def main():
    '''
    llm_wrapper = OllamaHelper("llama3:8b", "../", "llama3:8b")

    with open(sensitive_file_path, 'r') as file:
        find_sensitive_prompt = file.read()
    with open(crucial_file_path, 'r') as file:
        find_crucial_prompt = file.read()
    with open(replace_file_path, 'r') as file:
        replace_prompt = file.read()

    obfuscator = ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, replace_prompt, llm_wrapper)
'''
    obfuscator = WrongObfuscator()
    with open("../log/json/tmp.json", 'r') as file:
        data = json.load(file)

    metrics = evaluate_with_obfuscators(data["data"], [obfuscator])

    print(metrics)


if __name__ == "__main__":
    main()

