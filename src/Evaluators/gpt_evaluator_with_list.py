import os
import sys


from dotenv import load_dotenv 
from logging import Logger
from typing import Dict, List, Tuple, Union, Self

load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import get_answer
from src.utils.string_utils import extract_number


class GPTWithListEvaluator(EvaluatorTemplate):

    query_prompt = """Grade the similarity between the following two texts on a scale of 0.0 to 1.0 with emphasis on technical terms changed with relative emojis. A score of 0.0 means the emojis are not relevant or there were technical words to change and it didn't (two exact same text with technical terms not changed would score 0.0). A score of 1.0 means all the technical terms were changed with relative emojis.
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>
    """
    answer_prompt = """give a number between 0.0 to 1.0 where 0.0 is not similar at all and 1.0 signifies that the texts are highly similar, discussing the same topic, sharing the same opinion, and covering the same key details. The two following texts:
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>"""
    
    def __init__(self, logger: Logger ,prompt_path: str) -> Self:
        self.logger = logger


    def _find_leftovers(obfuscated_prompt, terms: List[str]) -> float:
            count = 0
            for term in terms:
                if term in obfuscated_prompt:
                    count += 1
            return 1-count/len(terms)
    
    def evaluate_prompt(self, obfuscated_prompt: str, case_data: Dict[str, Union[str, List[str]]]) -> Tuple[str, Dict[str, float]]:    #add return llm answer reasoning
        query = self.query_prompt.format(text1=case_data["original_question"], text2=obfuscated_prompt) 
        answer = get_answer(query)
        missed_precentage = GPTWithListEvaluator._find_leftovers(obfuscated_prompt, case_data["list"])
        self.logger.info(f"""evaluate_prompt
Prompt: {query}
Answer: {answer}
Extracted Answer: {extract_number(answer)}""")
        return answer, {"similarity": extract_number(answer), "replaced terms": missed_precentage}

    def evaluate_answer(self, obfuscated_answer: str, original_answer: Dict[str, Union[str, List[str]]]) -> Tuple[str, float]:
        query = self.answer_prompt.format(text1=obfuscated_answer, text2=original_answer)
        answer = get_answer(query)
        self.logger.info(f"""evaluate_answer
Prompt: {query}
Answer: {answer}
Extracted Answer: {extract_number(answer)}""")
        return answer, extract_number(answer)
    
