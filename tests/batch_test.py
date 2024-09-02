from datetime import datetime
import os
import sys
import json
import logging
from typing import Callable, List, Dict, Union, Tuple
from itertools import chain

from dotenv import load_dotenv 

load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from batch_evaluate import evaluate_batch

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import AzureClient
from src.utils.ollama_client import OllamaClient

from src.Obfuscators.single_prompt_obfuscator import SinglePromptObfuscator, make_single_prompt_obfuscator
from src.Obfuscators.few_prompt_obfuscator import FewPromptsObfuscator, make_few_prompts_obfuscator
from src.Obfuscators.three_prompt_obfuscator import ThreePromptsObfuscator, make_three_prompts_obfuscator
from src.Obfuscators.fake_obfuscator import FakeObfuscator, make_fake_obfuscator
from src.Obfuscators.wrong_obfuscator import WrongObfuscator, make_wrong_obfuscator
from src.Obfuscators.random_text import RandomText, make_random_text
from src.Obfuscators.smart_random_emoji import SmartRandom, make_smart_random
from src.Obfuscators.context_reletive_obfuscator import ContextReletiveObfuscator, make_context_reletive_obfuscator
from src.Obfuscators.context_only_obfuscator import ContextOnlyObfuscator, make_context_only_obfuscator
from src.Obfuscators.dictonary_obfuscator import DictonaryObfuscator, make_dict_obfuscator
from src.Obfuscators.obfuscator_template import Obfuscator

from src.Evaluators.gpt_evaluator_with_list import GPTWithListEvaluator
from src.Evaluators.list_embedding_evaluator import ListEmbeddingEvaluator
from src.Evaluators.gpt_and_embedding_evaluator import GPTAndEmbeddingEvaluator
from src.Evaluators.llm_embedding_and_precentage_of_change_evaluator import GPTEmbeddingAndPChangedEvaluator


single_query_file = "single_query_for_dict_v2.txt"
two_query_file_1 = "first_querry.txt"
two_query_file_2 = "second_querry.txt"
two_query_file_2_with_list = "second_querry_with_list.txt"
two_query_random_emojis = "second_querry_random_emoji.txt"

prompt_folder = os.path.join(os.getenv("PROJECT_PATH"),"src","Obfuscators","prompts")
sensitive_file_path =os.path.join(prompt_folder,"naive","extract_terms_prompt.txt")
crucial_file_path =os.path.join(prompt_folder,"naive","crucial_prompt.txt")
dictionary_file_path =os.path.join(prompt_folder,"naive","dictionary_prompt.txt")
single_prompt_path = os.path.join(prompt_folder,"single_querry", single_query_file)
two_prompt_1_path = os.path.join(prompt_folder,"two_querries", two_query_file_1)
two_prompt_2_path = os.path.join(prompt_folder,"two_querries", two_query_file_2)
two_prompt_2_with_list_path = os.path.join(prompt_folder,"two_querries", two_query_file_2_with_list)
two_query_random_emojis_path = os.path.join(prompt_folder,"two_querries", two_query_random_emojis)
log_path =os.path.join(os.path.dirname(__file__),"..","log","batch_test.log")

def prompt_loader(prompt_path: str) -> str:
    with open(prompt_path, 'r', encoding='utf-8') as file:
        return file.read()

def evaluate_with_obfuscators(data: list[dict], obfuscators: list[Obfuscator] ,logger: logging.Logger , evaluator_factory) -> list[list]:
    metrics = []
    logger.info(f"Starting evaluation {datetime.now()}")
    for i, (name, obfuscator) in enumerate(obfuscators):
        logger.info(f"Starting evaluation of {name}")
        print("evaluate_with_obfuscators: ",obfuscator().__class__.__name__)
        print(f"Starting evaluation of {name}")
        time = datetime.now()
        metrics.append([name, evaluate_batch(data[:50], obfuscator, logger, evaluator_factory)])

        output_folder_path = os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024", os.getenv("DATE"))
        json.dump(metrics, open(os.path.join(output_folder_path,"_checkpoint_" + name.replace(" ", "_") +".json"), "w") , indent=4)

        logger.info(f"time: {datetime.now()} finished evaluation of {name} in {datetime.now()-time}")
    return metrics


def main():
    disable_httpx_log = logging.getLogger("httpx")
    disable_httpx_log.setLevel(logging.WARNING)

    logging.basicConfig(filename=log_path, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting batch test")

    ollama_llm_wrapper_factory = lambda :OllamaClient("llama3:8b", "../", "llama3:8b", 0.0)
    azure_llm_wrapper_factory = lambda :AzureClient("azure_client",  "../", "gpt-4o-2024-05-13", 0.0)

    single_prompt_list = [prompt_loader(single_prompt_path)]
    two_prompt_list = [prompt_loader(two_prompt_1_path),prompt_loader(two_prompt_2_path)]
    three_prompt_list = [prompt_loader(sensitive_file_path),prompt_loader(crucial_file_path),prompt_loader(dictionary_file_path)]   
    smart_random_list = [prompt_loader(two_prompt_1_path)]
    context_reletive = [prompt_loader(two_prompt_1_path),prompt_loader(two_prompt_2_with_list_path)]

    cpprefix = "Do not explain the emojis in your answer and do not add new emojis that were not in the original question.\n"

    llm_wrapper_factories = {
        "ollama": ollama_llm_wrapper_factory,
        "azure": azure_llm_wrapper_factory
    }

    obfuscator_factories = {
        "FakeObfuscator": make_fake_obfuscator,
        # "WrongObfuscator": make_wrong_obfuscator,
        # "SmartRandom": make_smart_random,
        # "RandomText": make_random_text,
        # #"SinglePromptObfuscator": make_single_prompt_obfuscator,
        # "FewPromptsObfuscator": make_few_prompts_obfuscator,
        # "ThreePromptsObfuscator": make_three_prompts_obfuscator
        "ContextReletiveObfuscator": make_context_reletive_obfuscator,
        # "ContextOnlyObfuscator": make_context_only_obfuscator
        "DictionaryObfuscator": make_dict_obfuscator
    }

    obfuscators_details = [
        ("FakeObfuscator", {"name": "FakeObfuscator"}),
        # ("WrongObfuscator", {"name": "WrongObfuscator"}),
        # ("SmartRandom", {"name": "SmartRandom", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_list": smart_random_list, "prompt_prefix": cpprefix}),
        # ("RandomText", {"name": "RandomText", "llm_wrapper_factory": llm_wrapper_factories["azure"]}),
        # ("FewPromptsObfuscator", {"name": "TwoPromptObfuscator", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_list": two_prompt_list, "prompt_prefix": cpprefix}),
        # ("ThreePromptsObfuscator", {"name": "ThreePromptObfuscator", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_list": three_prompt_list, "prompt_prefix": cpprefix})
        ("ContextReletiveObfuscator", {"name": "ContextReletiveObfuscator", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_list": context_reletive, "prompt_prefix": cpprefix}),
        ("DictionaryObfuscator", {"name": "DictionaryObfuscator", "path": os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024", os.getenv("DATE"),"finance_combined_dictonary.json")})
        # ("ContextOnlyObfuscator", {"name": "ContextOnlyObfuscator", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_list": context_reletive, "prompt_prefix": cpprefix})
    ]

    loaded_obfuscators = []

    for obfuscator_name, args in obfuscators_details:
        loaded_obfuscators.append((obfuscator_name, obfuscator_factories[obfuscator_name](args)) )

    
    data_to_use = "finance_data_set.json"

    inputfile_path = os.path.join(os.getenv("PROJECT_PATH"),"data", "September-2024", os.getenv("DATE") ,data_to_use)
    with open(inputfile_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "", "gpt_evaluator", "gpt_evaluator_promt.txt")
    evaluator = lambda : GPTEmbeddingAndPChangedEvaluator()


    metrics = evaluate_with_obfuscators(data[45:], loaded_obfuscators, logger, evaluator)

    metrics_filename = "FINANCE_RESULTS_" + str(datetime.now()).replace(' ', '_').replace(':', '_') + ".json"
    output_folder_path = os.path.join(os.getenv("PROJECT_PATH"),"data", "September-2024", os.getenv("DATE"))
    os.makedirs(output_folder_path,exist_ok=True)
    json.dump(metrics, open(os.path.join(output_folder_path,metrics_filename), "w", encoding = 'utf-8'), ensure_ascii= False , indent=4)

    print("results saved to ", metrics_filename)


if __name__ == "__main__":
    main()


