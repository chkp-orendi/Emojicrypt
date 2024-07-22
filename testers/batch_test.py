from datetime import datetime
from batch_evaluate import evaluate_batch
import os
import sys
import json
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../libraries'))
#TODO: proper module structure
from ThreePromptObfuscator import ThreePromptsObfuscator
from SinglePromptObfuscator import SinglePromptObfuscator
from fake_obfuscator import FakeObfuscator
from wrong_obfuscator import WrongObfuscator
from ollama_helper import OllamaHelper


path_separator = os.path.sep


data_to_use = os.path.join("GPT4Temp0","enriched_generated_data_1.json")

sensitive_file_path =os.path.join(os.path.dirname(__file__),"prompts","naive","extract_terms_prompt.txt")
crucial_file_path = os.path.join(os.path.dirname(__file__),"prompts","naive","crucial_prompt.txt")
dictionary_file_path = os.path.join(os.path.dirname(__file__),"prompts","naive","dictionary_prompt.txt")
single_prompt_path = os.path.join(os.path.dirname(__file__),"prompts","single_querry","single_querry_for_dict.txt")

log_path =os.path.join(os.path.dirname(__file__),"logs","batch_test.log")

def evaluate_with_obfuscators(data, obfuscators,logger):
    metrics = []
    for name, obfuscator in obfuscators:
        metrics.append((name, evaluate_batch(data, obfuscator, logger)))
    return metrics

def main():
    disable_httpx_log = logging.getLogger("httpx")
    disable_httpx_log.setLevel(logging.WARNING)

    logging.basicConfig(filename=log_path, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting batch test")

    ollama_llm_wrapper_factory = lambda :OllamaHelper("llama3:8b", "../", "llama3:8b")

    with open(sensitive_file_path, 'r', encoding='utf-8') as file:
        find_sensitive_prompt = file.read()
    with open(crucial_file_path, 'r', encoding='utf-8') as file:
        find_crucial_prompt = file.read()
    with open(dictionary_file_path, 'r', encoding='utf-8') as file:
        dictionary_prompt = file.read()

    with open(single_prompt_path, 'r', encoding='utf-8') as file:
        single_prompt = file.read()


    single_prompt_factory = lambda : SinglePromptObfuscator(single_prompt, ollama_llm_wrapper_factory, logger)
    three_prompts_factory = lambda : ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, ollama_llm_wrapper_factory,logger)

    obfuscators = []
    #obfuscators.append(("WrongObfuscator", WrongObfuscator()))
    #obfuscators.append(("FakeObfuscator", FakeObfuscator()))
    obfuscators.append(("SinglePromptObfuscator", single_prompt_factory))
    obfuscators.append(("ThreePromptsObfuscator", three_prompts_factory))


    inputfile_path = os.path.join(os.path.dirname(__file__),"..","log","json", data_to_use)
    with open(inputfile_path, 'r') as file:
        data = json.load(file)

    metrics = evaluate_with_obfuscators(data[:2], obfuscators, logger)

    metrics_filename = str(datetime.now()).replace(' ', '_').replace(':', '_') + "-metrics.json"
    json.dump(metrics, open(os.path.join(os.path.dirname(__file__), "metrics", metrics_filename), "w"), indent=4)
    print("results saved to ", metrics_filename)


if __name__ == "__main__":
    main()


