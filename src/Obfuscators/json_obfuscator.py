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
from src.utils.string_utils import normalize, extract_context, extract_question, extract_json_list, extract_json_dict, extract_dict, smart_replace, break_word_characters_without_bracket
from src.utils.azure_client import get_json_with_histroy


def make_json_obfuscator(args: Dict):
    return lambda: JsonObfuscator(name = args["name"],
                                        llm_wrapper_factory=args["llm_wrapper_factory"],
                                        prompt_list=args["prompt_list"],
                                        prompt_prefix=args["prompt_prefix"],
                                        percentage = args["percentage"])

class JsonObfuscator(Obfuscator):
    """
    This obfuscator will ask llm for a json format.
    Right now supports only azure api, but possible to add ollama.
    """
    def __init__(self, name: str, llm_wrapper_factory, prompt_list: list, prompt_prefix="", percentage = 20):
        self._prompt_list = prompt_list[0]
        self._prompt_dict = prompt_list[1]
        self._llm_wrapper_factory = llm_wrapper_factory
        self._term_list = []
        self._dictionary_used = {}
        self._prompt_prefix = prompt_prefix
        self._percentage = percentage
        self._logger = getLogger("__main__")
        super().__init__(name)


    def _extract_terms(self, user_prompt):
        messages =[
            {
                "role": "system",
                "content": f"""You are a machine that given a text will return a list of technical terms in the format $LIST: [ex1, ex2, ...]
The user will tell you how many words [low, mediume, hight] to return and you will do your best to return the number of words required from you."""
            },
            {
                "role": "user",
                "content": self._prompt_list.format(text=user_prompt, percentage=self._percentage)
            }
        ]
        self._messages = messages
        response_text = get_json_with_histroy(messages)
        self._messages.append({
            "role": "assistant",
            "content": response_text
            })
        self._term_list = extract_json_list(response_text)

    def _fix_list(self, terms_list: list):
        key_word_list = [term for term in terms_list if term in self.question.split(''.join(break_word_characters_without_bracket)) and term not in self.context.split(''.join(break_word_characters_without_bracket))]
        self._term_list = [term for term in terms_list if term not in key_word_list]


    def _fix_dict(self, dictionary: dict):
        new_dict = {}
        for key, value in dictionary.items():
            match = re.search(r'\((.*?)\)', key)
            if match:
                word = match.group(1)
                new_key = re.sub(r'\s*\(.*?\)', '', key).strip()  # Remove "(word)" and any surrounding spaces
                new_dict[new_key] = value
                # new_dict[word] = value
                # new_dict[key] = value
            else:
                new_dict[key] = value
        return new_dict

            

    def _extract_dict(self):
        self._messages.append({
            "role": "user",
            "content": self._prompt_dict.format(lst=self._term_list)
        })

        response_text = get_json_with_histroy(self._messages)       
        extracted_dict = extract_json_dict(response_text)
        # fixed_dict = self._fix_dict(extracted_dict)
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


