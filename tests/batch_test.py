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
from src.Obfuscators.json_obfuscator import JsonObfuscator, make_json_obfuscator
from src.Obfuscators.phase_1_obfuscator import PhaseOneObfuscator, make_phase_one_obfuscator
from src.Obfuscators.obfuscator_template import Obfuscator

from src.Evaluators.gpt_evaluator_with_list import GPTWithListEvaluator
from src.Evaluators.list_embedding_evaluator import ListEmbeddingEvaluator
from src.Evaluators.gpt_and_embedding_evaluator import GPTAndEmbeddingEvaluator
from src.Evaluators.llm_embedding_and_precentage_of_change_evaluator import GPTEmbeddingAndPChangedEvaluator
from src.Evaluators.phase_1_eval import Phase_1_Evaluator




def prompt_loader(prompt_path: str) -> str:
    with open(prompt_path, 'r', encoding='utf-8') as file:
        return file.read()

   
def init_log():
    disable_httpx_log = logging.getLogger("httpx")
    disable_httpx_log.setLevel(logging.WARNING)

    logging.basicConfig(filename=log_path, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting batch test")


def load_data() -> json:
    data_to_use = "software development data set.json"
    inputfile_path = os.path.join(os.getenv("PROJECT_PATH"),"data", "September-2024", "2024-09-09" ,data_to_use)
    with open(inputfile_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def run_test(data: json, obfuscators: list[Callable[[],Obfuscator]], evaluator_factory: EvaluatorTemplate):
    metrics = []
    # logger.info(f"Starting evaluation {datetime.now()}")
    for i, (name, obfuscator) in enumerate(obfuscators):
        # logger.info(f"Starting evaluation of {name}")
        print("evaluate_with_obfuscators: ",obfuscator().get_name())
        print(f"Starting evaluation of {obfuscator().get_name()}")
        time = datetime.now()
        metrics.append([obfuscator().get_name(), evaluate_batch(data, obfuscator, evaluator_factory)])

        output_folder_path = os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024", os.getenv("DATE"))
        json.dump(metrics, open(os.path.join(output_folder_path,"_checkpoint_" + name.replace(" ", "_") +".json"), "w") , indent=4)

        # logger.info(f"time: {datetime.now()} finished evaluation of {name} in {datetime.now()-time}")
    
    return metrics
    

def get_evalutor() -> Callable[[], EvaluatorTemplate]:
    return lambda: Phase_1_Evaluator()

def load_obfuscators_data():
    global cpprefix
    global single_prompt_list
    global two_prompt_list
    global two_prompt_json_list
    global two_prompt_json_high_p_list
    global three_prompt_list
    global smart_random_p_list
    global smart_random_high_p_list
    global two_prompt_smart_random_low_p_path
    global two_prompt_smart_random_high_p_path
    global context_reletive
    global two_prompt_json_low_p_list
    global context_reletive_replace_alot
    global context_reletive_around_p

    cpprefix = """
Do not explain the emojis in your answer and other than the exact emoji sequences from the original prompt, do not use emojis in your answer.\n
"""
#     cpprefix = """
# Consider the following restriction to the following question:
# 1. Do not explain the emojis in your answer.
# 2. Other than the exact emoji sequences from the original prompt do not use emojis in your answer.
# """
    
    
    single_query_file = "single_query_for_dict_v2.txt"
    two_query_file_1 = "first_querry.txt"
    two_query_file_2 = "second_querry.txt"
    two_query_file_2_with_list = "second_querry_with_list.txt"
    two_query_random_emojis = "second_querry_random_emoji.txt"

    first_querry_json_with_percentage = "first_querry_json_with_percentage.txt"
    first_querry_high_p = "first_querry_high_p.txt"
    first_querry_low_p = "first_querry_low_p.txt"
    
    second_querry_json_with_list = "second_querry_json_with_list.txt"

    prompt_folder = os.path.join(os.getenv("PROJECT_PATH"),"src","Obfuscators","prompts")
    sensitive_file_path =os.path.join(prompt_folder,"naive","extract_terms_prompt.txt")
    crucial_file_path =os.path.join(prompt_folder,"naive","crucial_prompt.txt")
    dictionary_file_path =os.path.join(prompt_folder,"naive","dictionary_prompt.txt")
    single_prompt_path = os.path.join(prompt_folder,"single_querry", single_query_file)
    two_prompt_1_path = os.path.join(prompt_folder,"two_querries", two_query_file_1)
    two_prompt_smart_random_low_p_path = os.path.join(prompt_folder,"two_querries", "first_querry_low_p.txt")
    two_prompt_smart_random_high_p_path = os.path.join(prompt_folder,"two_querries", "first_querry_high_p.txt")
    two_prompt_1_alot_of_changes_path = os.path.join(prompt_folder,"two_querries", "first_querry_high_p.txt")
    two_prompt_1_around_p_path = os.path.join(prompt_folder,"two_querries", "first_querry_around_p.txt")
    two_prompt_2_path = os.path.join(prompt_folder,"two_querries", two_query_file_2)
    two_prompt_2_with_list_path = os.path.join(prompt_folder,"two_querries", two_query_file_2_with_list)
    

    first_querry_json_with_percentage_path = os.path.join(prompt_folder,"two_querries", "json_two_querries", first_querry_json_with_percentage)
    first_querry_json_high_p_path = os.path.join(prompt_folder,"two_querries", "json_two_querries", first_querry_high_p)
    first_querry_json_low_p_path = os.path.join(prompt_folder,"two_querries", "json_two_querries", first_querry_low_p)
    second_querry_json_with_list_path = os.path.join(prompt_folder,"two_querries", "json_two_querries", second_querry_json_with_list)
    
    
    log_path =os.path.join(os.path.dirname(__file__),"..","log","batch_test.log")

    single_prompt_list = [prompt_loader(single_prompt_path)]
    two_prompt_list = [prompt_loader(two_prompt_1_path),prompt_loader(two_prompt_2_path)]
    two_prompt_json_list = [prompt_loader(first_querry_json_with_percentage_path),prompt_loader(second_querry_json_with_list_path)]
    two_prompt_json_high_p_list = [prompt_loader(first_querry_json_high_p_path),prompt_loader(second_querry_json_with_list_path)]
    two_prompt_json_low_p_list = [prompt_loader(first_querry_json_low_p_path),prompt_loader(second_querry_json_with_list_path)]
    three_prompt_list = [prompt_loader(sensitive_file_path),prompt_loader(crucial_file_path),prompt_loader(dictionary_file_path)]   
    smart_random_p_list = [prompt_loader(two_prompt_smart_random_low_p_path)]
    smart_random_high_p_list = [prompt_loader(two_prompt_smart_random_high_p_path)]
    context_reletive = [prompt_loader(two_prompt_1_path),prompt_loader(two_prompt_2_with_list_path)]
    context_reletive_replace_alot = [prompt_loader(two_prompt_1_alot_of_changes_path),prompt_loader(second_querry_json_with_list_path)]
    context_reletive_around_p = [prompt_loader(two_prompt_1_around_p_path),prompt_loader(second_querry_json_with_list_path)]

def get_obfuscators() -> list[Obfuscator]:
    load_obfuscators_data()
    obfuscator_factories = {
    "FakeObfuscator": make_fake_obfuscator,
    # "WrongObfuscator": make_wrong_obfuscator,
    "SmartRandom": make_smart_random,
    # "RandomText": make_random_text,
    # #"SinglePromptObfuscator": make_single_prompt_obfuscator,
    # "FewPromptsObfuscator": make_few_prompts_obfuscator,
    # "ThreePromptsObfuscator": make_three_prompts_obfuscator
    "ContextReletiveObfuscator": make_context_reletive_obfuscator,
    # "ContextOnlyObfuscator": make_context_only_obfuscator
    "DictionaryObfuscator": make_dict_obfuscator,
    "JsonObfuscator": make_json_obfuscator,
    "PhaseOneObfuscator": make_phase_one_obfuscator
    }

    obfuscators_details = [
        # ("ContextReletiveObfuscator", {"name": "ContextReletiveObfuscator - 5", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": context_reletive_around_p, "prompt_prefix": cpprefix, "percentage": 5}),
        # ("ContextReletiveObfuscator", {"name": "ContextReletiveObfuscator - 20", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": context_reletive_around_p, "prompt_prefix": cpprefix, "percentage": 20}),
        # ("ContextReletiveObfuscator", {"name": "ContextReletiveObfuscator - 40", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": context_reletive_around_p, "prompt_prefix": cpprefix, "percentage": 40}),
        # ("ContextReletiveObfuscator", {"name": "ContextReletiveObfuscator - 80", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": context_reletive_around_p, "prompt_prefix": cpprefix, "percentage": 80}),
        # ("FakeObfuscator", {"name": "FakeObfuscator"}),
        # ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - ollama - 80", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_prefix": cpprefix, "lower_bound_percentage": 75, "upper_bound_percentage": 85}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 95", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 90, "upper_bound_percentage": 100}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 90", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 85, "upper_bound_percentage": 95}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 80", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 75, "upper_bound_percentage": 85}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 70", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 65, "upper_bound_percentage": 75}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 60", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 55, "upper_bound_percentage": 65}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 50", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 45, "upper_bound_percentage": 55}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 40", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 35, "upper_bound_percentage": 45}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 30", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 25, "upper_bound_percentage": 35}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 20", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 15, "upper_bound_percentage": 25}),
        ("PhaseOneObfuscator", {"name": "PhaseOneObfuscator - azure - 10", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_prefix": cpprefix, "lower_bound_percentage": 5, "upper_bound_percentage": 15}),
        # # # ("WrongObfuscator", {"name": "WrongObfuscator"}),
        # ("SmartRandom", {"name": "SmartRandom - 5", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": smart_random_p_list, "prompt_prefix": cpprefix, "percentage": 5}),
        # ("SmartRandom", {"name": "SmartRandom - 20", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": smart_random_p_list, "prompt_prefix": cpprefix, "percentage": 20}),
        # ("SmartRandom", {"name": "SmartRandom - 40", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": smart_random_p_list, "prompt_prefix": cpprefix, "percentage": 40}),
        # ("SmartRandom", {"name": "SmartRandom - 90", "llm_wrapper_factory": llm_wrapper_factories["ollama"], "prompt_list": smart_random_p_list, "prompt_prefix": cpprefix, "percentage": 90}),
        # ("ContextReletiveObfuscator", {"name": "ContextReletiveObfuscator - 80 azure", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_list": context_reletive_around_p, "prompt_prefix": cpprefix, "percentage": 80}),
        # ("ContextReletiveObfuscator", {"name": "ContextReletiveObfuscator - 95 azure", "llm_wrapper_factory": llm_wrapper_factories["azure"], "prompt_list": context_reletive_around_p, "prompt_prefix": cpprefix, "percentage": 95})
    ]

    loaded_obfuscators = []

    for obfuscator_name, args in obfuscators_details:
        loaded_obfuscators.append((obfuscator_name, obfuscator_factories[obfuscator_name](args)) )
    return loaded_obfuscators

def init_clients():
    global llm_wrapper_factories

    ollama_llm_wrapper_factory = lambda :OllamaClient("llama3:8b", "../", "llama3:8b", 0.0)
    azure_llm_wrapper_factory = lambda :AzureClient("azure_client",  "../", "gpt-4o-2024-05-13", 0.0)
    llm_wrapper_factories = {
        "ollama": ollama_llm_wrapper_factory,
        "azure": azure_llm_wrapper_factory
    } 

def save_results(results: list, name: str):
    output_folder_path = os.path.join(os.getenv("PROJECT_PATH"),"data", "September-2024", os.getenv("DATE"))
    metrics_filename = name + str(datetime.now()).replace(' ', '_').replace(':', '_') + ".json"
    os.makedirs(output_folder_path,exist_ok=True)
    with open(os.path.join(output_folder_path,metrics_filename), "w", encoding = 'utf-8') as file:
        json.dump(results,file, ensure_ascii= False , indent=4)
    print("results saved to ", metrics_filename)

def main():
    # init_log()

    init_clients()
    obfuscators = get_obfuscators()
    data = load_data()
    evaluator_factory = get_evalutor()
    results = run_test(data, obfuscators, evaluator_factory)
    save_results(results, """testing""")



if __name__ == "__main__":
    main()