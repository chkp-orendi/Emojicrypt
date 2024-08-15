import os
import sys
from typing import Dict

from dotenv import load_dotenv 
from logging import Logger, getLogger
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import get_answer, get_embedding, cosine_similarity
from src.utils.answer_extraction import extract_number


class GPTAndEmbeddingEvaluator(EvaluatorTemplate):

    query_prompt = """Grade the similarity between the following two texts on a scale of 0.0 to 1.0 with emphasis on technical terms changed with relative emojis. A score of 0.0 means the emojis are not relevant or there were technical words to change and it didn't (two exact same text with technical terms not changed would score 0.0). A score of 1.0 means all the technical terms were changed with relative emojis.
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>
    """
    answer_prompt = """give a number between 0.0 to 1.0 where 0.0 is not similar at all and 1.0 signifies that the texts are highly similar, discussing the same topic, sharing the same opinion, and covering the same key details. The two following texts:
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>"""
    
    def __init__(self):
        self.logger = getLogger("__main__")

    def evaluate_prompt(self, obfuscated_prompt: str, original_prompt: Dict):
        query = self.query_prompt.format(text1=original_prompt["original_question"] ,text2=obfuscated_prompt) 
        answer = get_answer(query)
        llm_similarity = extract_number(answer)
        ada_similarity = cosine_similarity(original_prompt["original_question"], obfuscated_prompt)

        self.logger.info(f"""evaluate_prompt
Prompt: {query}
Answer: {answer}
llm_similarity: {llm_similarity}
ada_similarity: {ada_similarity}""")
        return answer, {"llm_similarity": llm_similarity, "ada_similarity": ada_similarity}

    def evaluate_answer(self, obfuscated_answer, original_answer):
        query = self.answer_prompt.format(text1=obfuscated_answer, text2=original_answer)        
        answer = get_answer(query)
        llm_similarity = extract_number(answer)
        ada_similarity = cosine_similarity(original_answer["original_answer"], obfuscated_answer)


        self.logger.info(f"""evaluate_answer
Prompt: {query}
Answer: {answer}
llm_similarity: {llm_similarity}
ada_similarity: {ada_similarity}""")
        return answer, {"llm_similarity": llm_similarity, "ada_similarity": ada_similarity}
    
