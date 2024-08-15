import re
from typing import Dict

import sys
import os
from dotenv import load_dotenv 
from logging import Logger, getLogger
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.answer_extraction import extract_dict, extract_list

def make_three_prompts_obfuscator(args: Dict):
    return lambda: ThreePromptsObfuscator(name = args["name"],
                                        llm_wrapper_factory=args["llm_wrapper_factory"],
                                        prompt_list=args["prompt_list"],
                                        prompt_prefix=args["prompt_prefix"])

class ThreePromptsObfuscator(Obfuscator):
    def __init__(self, name: str, llm_wrapper_factory, prompt_list: list, prompt_prefix=""):
        self._extract_terms_prompt = prompt_list[0]
        self._find_crucial_prompt = prompt_list[1]
        self._dictionary_prompt = prompt_list[2]
        self._llm_wrapper_factory = llm_wrapper_factory
        self._extracted_terms = []
        self._extracted_crucial = {}
        self._dictionary_used = {}
        self._prompt_prefix = prompt_prefix
        self._logger = getLogger("__main__")
        super().__init__(name)


    def _extract_terms(self, user_prompt):       
        response_text = self._llm_wrapper.send_query(self._extract_terms_prompt.format(text=user_prompt))
        return extract_list(response_text)

    def _find_crucial(self, user_prompt):
        response_text = self._llm_wrapper.send_query(self._find_crucial_prompt.format(text=user_prompt))
        self._logger.info("Crucial:" )
        self._logger.info(response_text)
        return set(extract_list(response_text))

    def _find_replacements(self, text, from_list):
        response_text = self._llm_wrapper.send_query(self._dictionary_prompt.format(text=text, words_list=from_list))
        return extract_dict(response_text)

    def obfuscate(self, user_prompt):
        self._llm_wrapper = self._llm_wrapper_factory()
        self._extracted_terms = self._extract_terms(user_prompt["original_question"])
        self._extracted_crucial = self._find_crucial(user_prompt["original_question"])
        self._extracted_terms = [item for item in self._extracted_terms if item not in self._extracted_crucial]
        self._dictionary_used = self._find_replacements(text=user_prompt["original_question"], from_list=self._extracted_terms)
        if len(self._dictionary_used) == 0:
            self._logger.info("Empty dictionary_used")
        else:
            self._logger.info("dictionary_used:" + str(self._dictionary_used))

        response_text = user_prompt["original_question"]
        for key, value in self._dictionary_used.items():
            response_text = response_text.replace(key, value)
            #response_text = re.sub(r'\b' + re.escape(key) + r'\b', value, response_text)
        return self._prompt_prefix + response_text

    def deobfuscate(self, obfuscated_answer):
        deobfuscated_answer = obfuscated_answer
        for key, value in self._dictionary_used.items():
            deobfuscated_answer = deobfuscated_answer.replace(value, key)
            #deobfuscated_answer = re.sub(r'\b' + re.escape(value) + r'\b', key, deobfuscated_answer)
        return deobfuscated_answer

def replace_words(text, replacements):
    for key in replacements.keys():
        text = text.replace(key, replacements[key])
    return text

if __name__ =="main":
    replace_words("hio", {"hio":"hello"})