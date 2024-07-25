from datetime import datetime
from batch_evaluate import evaluate_batch
import os
import sys
import json
import logging
import plotly

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libraries')))
from AzureApi import AzureHelper
from ollama_helper import OllamaHelper
from Obfuscators.single_prompt_obfuscator import SinglePromptObfuscator
from Obfuscators.three_prompt_obfuscator import ThreePromptsObfuscator
from Obfuscators.fake_obfuscator import FakeObfuscator
from Obfuscators.wrong_obfuscator import WrongObfuscator
from Obfuscators.few_prompt_obfuscator import FewPromptsObfuscator


data_to_use = "2024-07-24_12-00-00_dataset_good_take.json"

single_query_file = "single_query_for_dict_v2.txt"
two_query_file_1 = "first_querry.txt"
two_query_file_2 = "second_querry.txt"

sensitive_file_path =os.path.join(os.path.dirname(__file__),"prompts","naive","extract_terms_prompt.txt")
crucial_file_path = os.path.join(os.path.dirname(__file__),"prompts","naive","crucial_prompt.txt")
dictionary_file_path = os.path.join(os.path.dirname(__file__),"prompts","naive","dictionary_prompt.txt")
single_prompt_path = os.path.join(os.path.dirname(__file__),"prompts","single_querry", single_query_file)
two_prompt_1_path = os.path.join(os.path.dirname(__file__),"prompts","two_querries", two_query_file_1)
two_prompt_2_path = os.path.join(os.path.dirname(__file__),"prompts","two_querries", two_query_file_2)


log_path =os.path.join(os.path.dirname(__file__),"..","log","batch_test.log")
def evaluate_with_obfuscators(data, obfuscators,logger):
    metrics = []
    for name, obfuscator in obfuscators:
        logger.info(f"Starting evaluation of {name}")
        metrics_filename = str(datetime.now()).replace(' ', '_').replace(':', '_') + "-metrics" + name + ".json"
        metrics.append((name, evaluate_batch(data, obfuscator, logger)))
        json.dump(metrics, open(os.path.join(os.path.dirname(__file__), "metrics", metrics_filename), "w"), indent=4)
    return metrics

def main():
    disable_httpx_log = logging.getLogger("httpx")
    disable_httpx_log.setLevel(logging.WARNING)

    logging.basicConfig(filename=log_path, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting batch test")

    #ollama_llm_wrapper_factory = lambda :OllamaHelper("llama3:8b", "../", "llama3:8b", 0.0)
    azure_llm_wrapper_factory = lambda :AzureHelper("azure_client",  "../", "gpt-4o-2024-05-13", 0.0)

    with open(sensitive_file_path, 'r', encoding='utf-8') as file:
        find_sensitive_prompt = file.read()
    with open(crucial_file_path, 'r', encoding='utf-8') as file:
        find_crucial_prompt = file.read()
    with open(dictionary_file_path, 'r', encoding='utf-8') as file:
        dictionary_prompt = file.read()

    with open(single_prompt_path, 'r', encoding='utf-8') as file:
        single_prompt = file.read()
    with open(two_prompt_1_path, 'r', encoding='utf-8') as file:
        two_prompt_1 = file.read()
    with open(two_prompt_2_path, 'r', encoding='utf-8') as file:
        two_prompt_2 = file.read()


    single_prompt_factory = lambda : SinglePromptObfuscator(single_prompt, azure_llm_wrapper_factory, logger)
    two_obfuscator_factory = lambda : FewPromptsObfuscator([two_prompt_1,two_prompt_2], azure_llm_wrapper_factory, logger)
    three_prompts_factory = lambda : ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, azure_llm_wrapper_factory,logger)
    wrong_obfuscator_factory = lambda : WrongObfuscator()
    fake_obfuscator_factory = lambda : FakeObfuscator()

    obfuscators = []
    obfuscators.append(("WrongObfuscator", wrong_obfuscator_factory))
    obfuscators.append(("FakeObfuscator", fake_obfuscator_factory))
    obfuscators.append(("SinglePromptObfuscator", single_prompt_factory))
    obfuscators.append(("TwoPromptsObfuscator", two_obfuscator_factory))
    obfuscators.append(("ThreePromptsObfuscator", three_prompts_factory))

    inputfile_path = os.path.join(os.path.dirname(__file__),"..","data", "scripts_to_generate_data", data_to_use)
    with open(inputfile_path, 'r') as file:
        data = json.load(file)

    metrics = evaluate_with_obfuscators(data, obfuscators, logger)

    metrics_filename = str(datetime.now()).replace(' ', '_').replace(':', '_') + "-metrics.json"
    json.dump(metrics, open(os.path.join(os.path.dirname(__file__), "metrics", metrics_filename), "w"), indent=4)
    print("results saved to ", metrics_filename)


if __name__ == "__main__":
    main()


