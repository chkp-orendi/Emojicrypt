# %%
import os
import sys
import json
import logging
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.utils.azure_client import AzureClient, get_answer
from src.utils.answer_extraction import smart_replace

from src.Evaluators.gpt_evaluator import GPTEvaluator

from src.Obfuscators.few_prompt_obfuscator import FewPromptsObfuscator
from src.Obfuscators.fake_obfuscator import FakeObfuscator
from src.Obfuscators.wrong_obfuscator import WrongObfuscator
from src.Obfuscators.random_text import RandomText
from src.Obfuscators.totally_random_emoji import TotallyRandomEmoji




# %%
disable_httpx_log = logging.getLogger("httpx")
disable_httpx_log.setLevel(logging.WARNING)
logging.basicConfig(filename="random_log", level=logging.INFO)
logger = logging.getLogger(__name__)

# %%
two_prompt_1_path = os.path.join(os.getenv("PROJECT_PATH"),"src","Obfuscators","prompts","two_querries", "first_querry.txt")
two_prompt_2_path = os.path.join(os.getenv("PROJECT_PATH"),"src","Obfuscators","prompts","two_querries", "second_querry_random_emoji.txt")

azure_llm_wrapper_factory = lambda :AzureClient("azure_client",  "../", "gpt-4o-2024-05-13", 0.0)
with open(two_prompt_1_path, 'r', encoding='utf-8') as file:
    two_prompt_1 = file.read()
with open(two_prompt_2_path, 'r', encoding='utf-8') as file:
    two_prompt_2 = file.read()


cpprefix = "Do not explain the emojis in your answer.\n"
smart_random_emoji = lambda : FewPromptsObfuscator([two_prompt_1,two_prompt_2], azure_llm_wrapper_factory, logger, cpprefix)
totally_random_emoji = lambda : TotallyRandomEmoji()
random_text = lambda : RandomText(azure_llm_wrapper_factory)
fake_obfuscator = lambda : FakeObfuscator()
wrong_obfuscator = lambda : WrongObfuscator()
three_prompt_gpt_evaluator = GPTEvaluator(logger, "..")


gpt_evaluator = GPTEvaluator(logger, "..")

# %%
data_to_use = "RESULTS_2024-08-07_10_46_47.771852gpt_metric_new_test.json"
inputfile_path = os.path.join(os.getenv("PROJECT_PATH"),"data",data_to_use)
with open(inputfile_path, 'r') as file:
    data = json.load(file)

# %%
original_prompt = "How does the use of machine learning algorithms in predictive analytics enhance decision-making processes in businesses, and what are some common challenges faced during implementation? BE CONCISE"
original_answer = "Machine learning algorithms enhance decision-making in businesses by analyzing large datasets to identify patterns, predict outcomes, and provide actionable insights. This leads to more informed, data-driven decisions, improved efficiency, and competitive advantages.\n\nCommon challenges during implementation include:\n\n1. **Data Quality**: Incomplete or inaccurate data can lead to poor model performance.\n2. **Complexity**: Developing and tuning models requires specialized skills and knowledge.\n3. **Integration**: Incorporating machine learning systems into existing workflows and IT infrastructure can be difficult.\n4. **Scalability**: Ensuring models perform well as data volume grows.\n5. **Bias**: Models can perpetuate or amplify existing biases in data.\n6. **Cost**: High initial investment in technology and talent.\n\nAddressing these challenges requires careful planning, ongoing monitoring, and a commitment to data governance and ethical practices."

# %%
results_arr = []
for i in range (5):
    obfuscator = wrong_obfuscator()
    obfuscated_prompt = obfuscator.obfuscate(original_prompt)
    prompt_evaluation = gpt_evaluator.evaluate_prompt(original_prompt, obfuscated_prompt)
    answer = get_answer(obfuscated_prompt)
    deobfuscated_answer = obfuscator.deobfuscate(answer)
    answer_evaluation = gpt_evaluator.evaluate_answer(original_answer, deobfuscated_answer)
    print(f"""________________________________________
prompt_evaluation: {prompt_evaluation}
answer_evaluation: {answer_evaluation}
________________________________________""")
    results_arr.append(prompt_evaluation)


