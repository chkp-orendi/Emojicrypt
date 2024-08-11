from typing import Callable, Self
import sys
import os
from logging import Logger
from dotenv import load_dotenv 
from random import randrange
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.answer_extraction import extract_list, smart_replace
class SmartRandom(Obfuscator):
    random_emojis = """
🐋🐍🎺🐊🎨🦀🐩🦉🎬🦏🐦🐗🐼🎸🐃🐌🐱🦅🐡🐑🐰🎭🦉🎷🎲🐝🎸🦀🎥🐜🦄🎮🎃🐢🐻🎮🎲🎮🐰🐺🎮🐹🎧🎺🎮🦄🎨🐭🎸🐠🐨🐛🦐🐟🐦🎤🎲🐼🦀🐭🐬🐾🐒🎥🐰🦀🐭🐡🐢🐿🐋🐿🐨🐻🐱🎈🦊🐣🎃🦁🐂🎧🎃🎥🐶🐍🎲🐮🎤🐘🎨🎸🐰🎭🎤🐧🎸🦄🦇🦎🐺🎥🐭🎷🦁🐦🎃🎶🐢🎹🦋🎮🦀🎤🐸🎷🐠🎶🎲🐦🎨
"""

    def __init__(self: Self, prompt : str, llm_wrapper_factory: Callable[[],Obfuscator], logger: Logger, prompt_prefix: str ="" ) -> None:
        self._prompt = prompt
        self._llm_wrapper_factory = llm_wrapper_factory
        self._logger = logger
        self._dictionary_used = {}
        self._prompt_prefix = prompt_prefix
        self._list_of_technical_terms = []

    def get_list(self: Self, user_prompt: str) -> list[str]:
        answer = self._llm_wrapper.send_query(self._prompt + user_prompt)
        self._list_of_technical_terms = extract_list(answer)
        return self._list_of_technical_terms

    def init_for_prompt(self: Self) -> None:
        self._llm_wrapper = self._llm_wrapper_factory()
        self._dictionary_used = {}
        self._list_of_technical_terms = []

    def obfuscate(self: Self, user_prompt: dict[str,str | int | float | dict]) -> str:
        self.init_for_prompt()
        list_of_words = self.get_list(user_prompt["original_question"])
        for word in list_of_words:
            x = randrange(0, len(self.random_emojis)-4)
            y = randrange(1, 4)
            self._dictionary_used[word] = self.random_emojis[x:x+y]
        obfuscated_Text = smart_replace(user_prompt["original_question"], self._dictionary_used)
        return obfuscated_Text

    def deobfuscate(self: Self, obfuscated_answer: str) -> str:
        deobfuscated_Text = smart_replace(obfuscated_answer, {value:key for key,value in self._dictionary_used.items()})
        return deobfuscated_Text

    def get_dictionary(self: Self) -> dict[str,str]:
        return self._dictionary_used

