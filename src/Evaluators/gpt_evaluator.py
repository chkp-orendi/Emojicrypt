import os
import sys


from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import get_answer
from src.utils.answer_extraction import extract_number


class GPTEvaluator(EvaluatorTemplate):

    query_prompt = """Grade the similarity between the following two texts on a scale of 0.0 to 1.0 with emphasis on technical terms changed with relative emojis. A score of 0.0 means the emojis are not relevant or there were technical words to change and it didn't. A score of 1.0 means all the technical terms were changed with relative emojis.
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>
    """
    answer_prompt = """give a number between 0.0 to 1.0 where 0.0 is not similar at all and 1.0 is the exact same text for the similarity for these 2 texts:
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>"""
    
    def __init__(self, prompt_path):
        print("GPT EVALUATOR INIT")

    def evaluate_prompt(self, obfuscated_prompt, case_data):
        query = self.query_prompt.format(text1=case_data["original_question"], text2=obfuscated_prompt) 
        answer = get_answer(query)
        print("prompt _______________________________________________")
        print(answer)
        return extract_number(answer)

    def evaluate_answer(self, obfuscated_answer, case_data):
        query = self.answer_prompt.format(text1=obfuscated_answer, text2=case_data["original_answer"])
        answer = get_answer(query)
        print("answer _______________________________________________")
        print(answer)
        return extract_number(answer)
    

evaluator = GPTEvaluator("prompt_path")

text1 = "a quick brown fox jumps over the lazy dog"
text2 = "a quick red fox jumps over the lazy dog"

evaluator.evaluate_prompt(text1, {"original_question": text2})