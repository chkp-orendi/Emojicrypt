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


path_separator = os.path.sep

sensitive_file_path =os.path.join(os.path.dirname(__file__),"prompts","naive","extract_terms_prompt.txt")
crucial_file_path = os.path.join(os.path.dirname(__file__),"prompts","naive","crucial_prompt.txt")
dictionary_file_path = os.path.join(os.path.dirname(__file__),"prompts","naive","dictionary_prompt.txt")

log_path =os.path.join(os.path.dirname(__file__),"logs","batch_test2.log")

def evaluate_with_obfuscators(data, obfuscators,logger):
    metrics = []
    for obfuscator in obfuscators:
        metrics.append(evaluate_batch(data, obfuscator,logger))
    return metrics

def main():
    disable_httpx_log = logging.getLogger("httpx")
    disable_httpx_log.setLevel(logging.WARNING)

    logging.basicConfig(filename=log_path, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting batch test")

    llm_wrapper = OllamaHelper("llama3:8b", "../", "llama3:8b")

    with open(sensitive_file_path, 'r', encoding='utf-8') as file:
        find_sensitive_prompt = file.read()
    with open(crucial_file_path, 'r', encoding='utf-8') as file:
        find_crucial_prompt = file.read()
    with open(dictionary_file_path, 'r', encoding='utf-8') as file:
        dictionary_prompt = file.read()

    obfuscator = ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, llm_wrapper,logger)

    #obfuscator = WrongObfuscator()
    data_to_use = "tmp.json"
    inputfile_path = os.path.join(os.path.dirname(__file__),"..","log","json", data_to_use)
    with open(inputfile_path, 'r') as file:
        data = json.load(file)

    metrics = evaluate_with_obfuscators(data[:10], [obfuscator], logger)

    print(metrics)


if __name__ == "__main__":
    main()

