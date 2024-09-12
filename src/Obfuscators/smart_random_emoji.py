from typing import Callable, Self, Dict
import sys
import os
from logging import Logger, getLogger
from dotenv import load_dotenv 
from random import randrange
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.string_utils import extract_list, smart_replace

import re

def make_smart_random(args: Dict) -> Callable:
    return lambda: SmartRandom(name = args["name"],
                                llm_wrapper_factory=args["llm_wrapper_factory"],
                                prompt_list=args["prompt_list"],
                                prompt_prefix=args["prompt_prefix"],
                                percentage=args["percentage"])

class SmartRandom(Obfuscator):
    random_emojis = """🐋🐍🎺🐊🎨🦀🐩🦉🎬🦏🐦🐗🐼🎸🐃🐌🐱🦅🐡🐑🐰🎭🦉🎷🎲🐝🎸🦀🎥🐜🦄🎮🎃🐢🐻🎮🎲🎮🐰🐺🎮🐹🎧🎺🎮🦄🎨🐭🎸🐠🐨🐛🦐🐟🐦🎤🎲🐼🦀🐭🐬🐾🐒🎥🐰🦀🐭🐡🐢🐿🐋🐿🐨🐻🐱🎈🦊🐣🎃🦁🐂🎧🎃🎥🐶🐍🎲🐮🎤🐘🎨🎸🐰🎭🎤🐧🎸🦄🦇🦎🐺🎥🐭🎷🦁🐦🎃🎶🐢🎹🦋🎮🦀🎤🐸🎷🐠🎶🎲🐦🎨"""

    def __init__(self, name: str, llm_wrapper_factory, prompt_list : str, prompt_prefix: str ="" , percentage = 70) -> Self:
        self._prompt = prompt_list[0]
        self._llm_wrapper_factory = llm_wrapper_factory
        self._logger = getLogger("__main__")
        self._dictionary_used = {}
        self._prompt_prefix = prompt_prefix
        self._list_of_technical_terms = []
        self._percentage = percentage
        super().__init__(name)


    def extract_old_list(self, text: str) -> list[str]:
        pattern = r"\$LIST:\s*\[(.*?)\]"

        matches = re.findall(pattern, text)
        if matches:
            match = matches[-1]
            return [token.strip("\"' \t\n") for token in match.split(',')]
        return []

    def get_list(self, user_prompt: str) -> list[str]:
        answer = self._llm_wrapper.send_query(self._prompt.format(text=user_prompt, percentage=self._percentage))

        self._list_of_technical_terms = self.extract_old_list(answer)
        return self._list_of_technical_terms

    def init_for_prompt(self) -> None:
        self._llm_wrapper = self._llm_wrapper_factory()
        self._dictionary_used = {}
        self._list_of_technical_terms = []

    def obfuscate(self, user_prompt: dict[str,str | int | float | dict]) -> str:
        self.init_for_prompt()
        list_of_words = self.get_list(user_prompt["original_prompt"])
        for word in list_of_words:
            y = randrange(1, 4)
            random_emoji = ""
            for i in range (y):
                x = randrange(0, len(self.random_emojis)-4)
                random_emoji += self.random_emojis[x]
            self._dictionary_used[word.strip('" \n')] = random_emoji
        obfuscated_Text = smart_replace(user_prompt["original_prompt"], self._dictionary_used)
        return obfuscated_Text

    def deobfuscate(self: Self, obfuscated_answer: str) -> str:
        deobfuscated_Text = smart_replace(obfuscated_answer, {value:key for key,value in self._dictionary_used.items()})
        return deobfuscated_Text

    def get_dictionary(self: Self) -> dict[str,str]:
        return self._dictionary_used

