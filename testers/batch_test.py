from batch_evaluate import evaluate_batch
import os
import sys
import json
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../libraries'))
#TODO: proper module structure
from ThreePromptObfuscator import ThreePromptsObfuscator
from fake_obfuscator import FakeObfuscator
from wrong_obfuscator import WrongObfuscator
from ollama_helper import OllamaHelper

sensitive_file_path = "prompts/naive/extract_terms_prompt.txt"
crucial_file_path = "prompts/naive/crucial_prompt.txt"
dictionary_file_path = "prompts/naive/dictionary_prompt.txt"

def evaluate_with_obfuscators(data, obfuscators,logger):
    metrics = []
    for obfuscator in obfuscators:
        metrics.append(evaluate_batch(data, obfuscator,logger))
    return metrics

def main():
    logging.basicConfig(filename="/root/Emoji/Emojicrypt/testers/batch_test.log", level=logging.INFO)
    logger = logging.getLogger(__name__)

    llm_wrapper = OllamaHelper("llama3:8b", "../", "llama3:8b")

    with open(sensitive_file_path, 'r') as file:
        find_sensitive_prompt = file.read()
    with open(crucial_file_path, 'r') as file:
        find_crucial_prompt = file.read()
    with open(dictionary_file_path, 'r') as file:
        dictiobary_prompt = file.read()

    obfuscator = ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictiobary_prompt, llm_wrapper,logger)

    #obfuscator = WrongObfuscator()
    with open("../log/json/tmp.json", 'r') as file:
        data = json.load(file)

    metrics = evaluate_with_obfuscators(data["data"], [obfuscator],logger)

    print(metrics)


if __name__ == "__main__":
    main()

