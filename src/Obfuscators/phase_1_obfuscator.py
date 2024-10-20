import re
from typing import Dict
import re
import sys
import os
from dotenv import load_dotenv 
from logging import Logger, getLogger
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.string_utils import normalize, extract_context, extract_question, extract_list, extract_dict, smart_replace, break_word_characters_without_bracket


list_prompt = """
Return a high number of technical terms, nouns, verbs and adjective from the text in a JSON list format. Ensure the list contains between {lower_bound_percentage}% to {upper_bound_percentage}% of the total words from the text.

1. The technical terms must appear in the text exactly as they are.
2. Do not include linking words in the list.
3. If both the singular and plural forms of a term appear in the text, add both.
4. It is crucial that the output contains {lower_bound_percentage}% to {upper_bound_percentage}% of the words from the original text, so please calculate this percentage accurately.
5. The list should not contain duplicates

Think carefully and explain how is the list you provided is between {lower_bound_percentage}% to {upper_bound_percentage}% of the words in the text. If it isn't, please provide a new list that meets the criteria.:
{text}
"""
dict_prompt = """
Given the following list {lst}
Provide an obfuscator for the words in relation to the context using very complex emojis sequence that are not straightforward and that will be very hard to understand. The keys and values shuld be UNIQUE.
Return in the format $Dict [value1:obfuscator1, value2: obfuscator2,....]

Now return $Dict on the list you provided
"""
# list_prompt = """
# Return a high number of technical terms, nouns, verbs and adjective from the text in a JSON list format. Ensure the list contains at least {lower_bound_percentage}% of the total words from the text.

# 1. The technical terms must appear in the text exactly as they are.
# 2. Do not include linking words in the list.
# 3. If both the singular and plural forms of a term appear in the text, add both.
# 4. It is crucial that the output contains at least {lower_bound_percentage}% of the words from the original text, so please calculate this percentage accurately.


# Think carefully and explain how is the list you provided contains at least {lower_bound_percentage}% of the words in the text. If it isn't, please provide a new list that meets the criteria.:
# {text}
# """
# dict_prompt = """
# Given the following list {lst}
# Provide an obfuscator for the words in relation to the context using very complex emojis sequence that are not straightforward and that will be very hard to understand. The keys and values shuld be UNIQUE.
# Return in the format $Dict [value1:obfuscator1, value2: obfuscator2,....]

# Now return $Dict on the list you provided
# """


def make_phase_one_obfuscator(args: Dict):
    return lambda: PhaseOneObfuscator(name = args["name"],
                                        llm_wrapper_factory=args["llm_wrapper_factory"],
                                        prompt_prefix=args["prompt_prefix"],
                                        lower_bound_percentage = args["lower_bound_percentage"],
                                        upper_bound_percentage = args["upper_bound_percentage"])

class PhaseOneObfuscator(Obfuscator):
    def __init__(self, name: str, llm_wrapper_factory, prompt_prefix="", lower_bound_percentage = 0, upper_bound_percentage = 0):
        self._llm_wrapper_factory = llm_wrapper_factory
        self._term_list = []
        self._dictionary_used = {}
        self._prompt_prefix = prompt_prefix
        self._lower_bound_percentage = lower_bound_percentage
        self._upper_bound_percentage = upper_bound_percentage
        self._term_list = []
        self._dictionary_used = {}
        self._logger = getLogger("__main__")
        super().__init__(name)


    def _extract_terms(self, user_prompt):       
        response_text = self._llm_wrapper.send_query(list_prompt.format(text=user_prompt, lower_bound_percentage=self._lower_bound_percentage, upper_bound_percentage=self._upper_bound_percentage), max_tokens= 4000)
        self._list_reasoning = response_text
        self._term_list = extract_list(response_text)
          

    def _extract_dict(self):
        response_text = self._llm_wrapper.send_query(dict_prompt.format(lst=self._term_list), max_tokens= 4000)  
        self._dict_reasoning = response_text
        extracted_dict = extract_dict(response_text)
        self._dictionary_used = extracted_dict

    def obfuscate(self, user_prompt):
        self._llm_wrapper = self._llm_wrapper_factory()
        self._extract_terms(user_prompt["original_prompt"])
        self._extract_dict()

        if len(self._dictionary_used) == 0:
            self._logger.info("Empty dictionary_used")
        else:
            self._logger.info("dictionary_used:" + str(self._dictionary_used))

        response_text = user_prompt["original_prompt"]
        response_text = smart_replace(response_text, self._dictionary_used)
        return self._prompt_prefix + response_text

    def deobfuscate(self, obfuscated_answer):
        deobfuscated_answer = obfuscated_answer
        deobfuscated_answer = smart_replace(deobfuscated_answer, {v:k for k,v in self._dictionary_used.items()})
        return deobfuscated_answer


