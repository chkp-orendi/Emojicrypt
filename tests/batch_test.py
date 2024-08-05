from datetime import datetime
from batch_evaluate import evaluate_batch
import os
import sys
import json
import logging


from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import AzureClient
from src.utils.ollama_client import OllamaClient
from src.Obfuscators.single_prompt_obfuscator import SinglePromptObfuscator
from src.Obfuscators.few_prompt_obfuscator import FewPromptsObfuscator
from src.Obfuscators.three_prompt_obfuscator import ThreePromptsObfuscator
from src.Obfuscators.fake_obfuscator import FakeObfuscator
from src.Obfuscators.wrong_obfuscator import WrongObfuscator

from src.Evaluators.gpt_evaluator import GPTEvaluator
from src.Evaluators.list_embedding_evaluator import ListEmbeddingEvaluator


single_query_file = "single_query_for_dict_v2.txt"
two_query_file_1 = "first_querry.txt"
two_query_file_2 = "second_querry.txt"



sensitive_file_path =os.path.join(os.getenv("PROJECT_PATH"),"src","Obfuscators","prompts","naive","extract_terms_prompt.txt")
crucial_file_path =os.path.join(os.getenv("PROJECT_PATH"),"src","Obfuscators","prompts","naive","crucial_prompt.txt")
dictionary_file_path =os.path.join(os.getenv("PROJECT_PATH"),"src","Obfuscators","prompts","naive","dictionary_prompt.txt")
single_prompt_path = os.path.join(os.path.dirname(__file__),"prompts","single_querry", single_query_file)
two_prompt_1_path = os.path.join(os.path.dirname(__file__),"prompts","two_querries", two_query_file_1)
two_prompt_2_path = os.path.join(os.path.dirname(__file__),"prompts","two_querries", two_query_file_2)


log_path =os.path.join(os.path.dirname(__file__),"..","log","batch_test.log")
def evaluate_with_obfuscators(data, obfuscators,logger, evaluator_factory):
    metrics = []
    logger.info(f"Starting evaluation {datetime.now()}")
    for i, (name, obfuscator) in enumerate(obfuscators):
        logger.info(f"Starting evaluation of {name}")
        time = datetime.now()
        metrics.append([name, evaluate_batch(data, obfuscator, logger, evaluator_factory)])
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

    with open(sensitive_file_path, 'r', encoding='utf-8') as file:
        find_sensitive_prompt = file.read()
    with open(crucial_file_path, 'r', encoding='utf-8') as file:
        find_crucial_prompt = file.read()
    with open(dictionary_file_path, 'r', encoding='utf-8') as file:
        dictionary_prompt = file.read()

    # with open(single_prompt_path, 'r', encoding='utf-8') as file:
    #     single_prompt = file.read()
    # with open(two_prompt_1_path, 'r', encoding='utf-8') as file:
    #     two_prompt_1 = file.read()
    # with open(two_prompt_2_path, 'r', encoding='utf-8') as file:
    #     two_prompt_2 = file.read()

    cpprefix = "Do not explain the emojis in your answer.\n"

    # single_prompt_factory = lambda : SinglePromptObfuscator(single_prompt, azure_llm_wrapper_factory, logger, cpprefix)
    # two_obfuscator_factory = lambda : FewPromptsObfuscator([two_prompt_1,two_prompt_2], azure_llm_wrapper_factory, logger, cpprefix)
    # three_prompts_factory = lambda : ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, ollama_llm_wrapper_factory,logger)
    # three_prompts_gpt_factory = lambda : ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, azure_llm_wrapper_factory,logger)
    three_prompts_prefix_factory = lambda : ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, azure_llm_wrapper_factory,logger, cpprefix)
    wrong_obfuscator_factory = lambda : WrongObfuscator()
    fake_obfuscator_factory = lambda : FakeObfuscator()
    # single_prompt_no_prefix_gpt4o_factory = lambda : SinglePromptObfuscator(single_prompt, azure_llm_wrapper_factory, logger)
    # two_obfuscator_no_prefix_gpt4o_factory = lambda : FewPromptsObfuscator([two_prompt_1,two_prompt_2], azure_llm_wrapper_factory, logger)
    # three_prompts_no_prefix_gpt4o_factory = lambda : ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, azure_llm_wrapper_factory,logger)
    # single_prompt_no_prefix_llama_factory = lambda : SinglePromptObfuscator(single_prompt, ollama_llm_wrapper_factory, logger)
    # two_obfuscator_no_prefix_llama_factory = lambda : FewPromptsObfuscator([two_prompt_1,two_prompt_2], ollama_llm_wrapper_factory, logger)
    # three_prompts_no_prefix_llama_factory = lambda : ThreePromptsObfuscator(find_sensitive_prompt, find_crucial_prompt, dictionary_prompt, ollama_llm_wrapper_factory,logger)





    obfuscators = []
    obfuscators.append(("WrongObfuscator", wrong_obfuscator_factory))
    obfuscators.append(("FakeObfuscator", fake_obfuscator_factory))
    #obfuscators.append(("SinglePromptObfuscator", single_prompt_factory))
    #obfuscators.append(("TwoPromptsObfuscator", two_obfuscator_factory))
    #obfuscators.append(("ThreePromptsObfuscatorLlama", three_prompts_factory))
    # obfuscators.append(("SinglePromptObfuscator - Llama3:8b", single_prompt_prefix_llama_factory))
    # obfuscators.append(("TwoPromptsObfuscator - Llama3:8b", two_obfuscator_prefix_llama_factory))
    #obfuscators.append(("ThreePromptsObfuscator - Llama3:8b", three_prompts_prefix_factory))

    # obfuscators.append(("SinglePrompt No Prefix Obfuscator - GPT-4o", single_prompt_no_prefix_gpt4o_factory))
    # obfuscators.append(("TwoPrompts No Prefix Obfuscator - GPT-4o", two_obfuscator_no_prefix_gpt4o_factory))
    # obfuscators.append(("ThreePrompts No Prefix Prefix Obfuscator - GPT-4o", three_prompts_no_prefix_gpt4o_factory))
    # obfuscators.append(("SinglePrompt No Prefix Obfuscator - Llama3:8b", single_prompt_no_prefix_llama_factory))
    # obfuscators.append(("TwoPrompts No Prefix Obfuscator - Llama3:8b", two_obfuscator_no_prefix_llama_factory))
    # obfuscators.append(("ThreePrompts No Prefix Obfuscator - Llama3:8b", three_prompts_no_prefix_llama_factory))



    data_to_use = "29-07-updated_answer.json"

    inputfile_path = os.path.join(os.getenv("PROJECT_PATH"),"data",data_to_use)
    with open(inputfile_path, 'r') as file:
        data = json.load(file)

    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "", "gpt_evaluator", "gpt_evaluator_promt.txt")
    evaluator = lambda : GPTEvaluator(prompt_path)

    metrics = evaluate_with_obfuscators(data, obfuscators, logger, evaluator)

    metrics_filename = "RESULTS_" + str(datetime.now()).replace(' ', '_').replace(':', '_') + "WrongFakeObf-gpt-evaluator.json"
    output_folder_path = os.path.join(os.getenv("PROJECT_PATH"),"data")
    os.makedirs(output_folder_path,exist_ok=True)
    json.dump(metrics, open(os.path.join(output_folder_path,metrics_filename), "w") , indent=4)

    print("results saved to ", metrics_filename)


if __name__ == "__main__":
    main()


