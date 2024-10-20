import os
import sys
from typing import Dict
import re

from dotenv import load_dotenv 
from logging import Logger, getLogger

import statistics

load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Evaluators.evaluator_template import EvaluatorTemplate
from src.utils.azure_client import get_answer, get_embedding, cosine_similarity
from src.utils.string_utils import extract_number, break_word_characters
from src.Evaluators.guess_obfuscators import guess_obfuscators
from src.utils.string_utils import smart_replace
"""
This evaluator contains most of the evaluations we used in phase 1 and will return all the details we want to keep to go over later (i.e llm answers).
Returns:
llm text answer

prompt_metric =  {
    "llm_score": ,
    "ada_similarity": ,
    "precentage_of_changed_word": ,
    "guessed_correct": 
}

answer_metric =  {
    "llm_score": ,
    "ada_similarity": ,
    "precentage_of_changed_word": ,
}

guessed_correct
number_of_emoji_in_prompt
llm_gussed_answer
"""


def precentage_of_changed_word_obfuscating(original_text: str, dictionary_used: dict):
    """
    Get precentage of changed words in the text.
    Dictionary is text to emoji mapping.
    """
    copy_text = original_text.lower()
    number_of_words = len(original_text.split())
    count = 0
    for key in sorted(dictionary_used.keys()):              
        matches = re.findall(rf'\b{re.escape(key.lower())}\b', copy_text)
        print(key, matches)
        if matches:
            copy_text = smart_replace(copy_text, {key.lower(): ""})
            count += len(matches) * len(key.split())
    return count/number_of_words


query_prompt = """Grade the similarity between the following two texts on a scale of 0.0 to 1.0 with emphasis on technical terms changed with relative emojis. A score of 0.0 means the emojis are not relevant or there were technical words to change and it didn't (two exact same text with technical terms not changed would score 0.0). A score of 1.0 means all the technical terms were changed with relative emojis.
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>
    """
answer_prompt = """give a number between 0.0 to 1.0 where 0.0 is not similar at all and 1.0 signifies that the texts are highly similar, discussing the same topic, sharing the same opinion, and covering the same key details. The two following texts:
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>"""

class Phase_1_Evaluator(EvaluatorTemplate):
    def __init__(self):
        self.logger = getLogger("__main__")

    
    
    def evaluate_prompt(self, obfuscated_prompt: str, case: dict) -> tuple[str,dict,dict]:
        """
output:
llm prompt score reasoning.
prompt score dictionary ={"llm_score":,
"ada_similarity":,
"precentage_of_changed_word":
}

guess evaluator dictionary = guess_results = {
    "llm_gussed_answer":,
    "guessed_correct":,
    "number_of_emoji_in_prompt": ,
    "correct_guesses_list: "
}
        
        """
        cpprefix = "Do not explain the emojis in your answer and do not add new emojis that were not in the original question.\n"

        obfuscated_prompt_without_prefix = obfuscated_prompt.replace(cpprefix, "")

        query = query_prompt.format(text1=case["original_prompt"] ,text2=obfuscated_prompt_without_prefix) 
        query_reverse_order = query_prompt.format(text1= obfuscated_prompt_without_prefix,text2=case["original_prompt"])

        answers = [get_answer(query), get_answer(query_reverse_order)]
        extracted_answers = [float(extract_number(answer)) for answer in answers]
        llm_similarity = statistics.mean(extracted_answers)
        obfuscated_prompt_embedding = get_embedding(obfuscated_prompt_without_prefix)

        ada_similarity = cosine_similarity(case["original_prompt_embedding"], obfuscated_prompt_embedding)

        llm_guessed_answer, guessed_correct, number_of_emoji_in_prompt, correct_guesses_list = guess_obfuscators(case["used_dictionary"],obfuscated_prompt_without_prefix, case["obfuscated_answer"])

        guess_results = {
            "llm_gussed_answer": llm_guessed_answer,
            "guessed_correct": guessed_correct,
            "number_of_emoji_in_prompt": number_of_emoji_in_prompt,
            "correct_guesses_list": correct_guesses_list
        }

        self.logger.info(f"""evaluate_prompt
Prompt: {query}
Answer: {answers}
llm_similarity: {llm_similarity}
ada_similarity: {ada_similarity}""")
        

        return answers, {"llm_score": llm_similarity, "ada_similarity": ada_similarity, "precentage_of_changed_word": precentage_of_changed_word_obfuscating(case["original_prompt"], case["used_dictionary"])}, guess_results

    def evaluate_answer(self, deobfuscated_answer: str, case: dict):
        query = answer_prompt.format(text1=deobfuscated_answer, text2=case["original_answer"])        
        query_reverse_order = answer_prompt.format(text1=case["original_answer"], text2=deobfuscated_answer)     
        answers = [get_answer(query), get_answer(query_reverse_order)]  
        extracted_answers = [float(extract_number(answer)) for answer in answers]
        llm_similarity = statistics.mean(extracted_answers)
        obfuscated_answer_embedding = get_embedding(answers[0])
        ada_similarity = cosine_similarity(case["original_answer_embedding"], obfuscated_answer_embedding)


        self.logger.info(f"""evaluate_answer
Prompt: {query}
Answer: {answers}
llm_similarity: {llm_similarity}
ada_similarity: {ada_similarity}""")
        
        return answers, {"llm_similarity": llm_similarity, "ada_similarity": ada_similarity}
