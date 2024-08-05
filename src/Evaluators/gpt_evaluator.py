import os
import sys


from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import get_answer
from src.utils.answer_extraction import extract_number


class GPTEvaluator(EvaluatorTemplate):

    query_prompt = """Grade the similarity between the following two texts on a scale of 0 to 100 with emphasis on tenchinical terms changed with reletive emojis. A score of 0 means the emojis are completely irrelevant or there were technical words to change and it didn't. A score of 100 means all the technical terms were changed with relative emojis or there were no technical terms to change.
    Text1: {text1}
    Text2: {text2}
    """
    answer_prompt = """give a number between 0-100 where 0 is not similar at all and 100 is the exact same text for the similarity for these 2 texts:
    Text 1 : {text1}
    Text 2 : {text2}"""
    
    def __init__(self, prompt_path):
        print("GPT EVALUATOR INIT")

    def evaluate_prompt(self, obfuscated_prompt, case_data):
        query = self.query_prompt.format(text1=obfuscated_prompt, text2=case_data["scenario"]) 
        answer = get_answer(query)
        print(answer)
        return extract_number(answer)

    def evaluate_answer(self, obfuscated_answer, case_data):
        query = self.answer_prompt.format(text1=obfuscated_answer, text2=case_data["original_answer"])
        answer = get_answer(query)
        return extract_number(answer)