import sys
import os
import json
from typing import Self
from dotenv import load_dotenv 
from logging import Logger, getLogger
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.string_utils import smart_replace
from typing import Dict, List, Union

load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator


def make_dict_obfuscator(args: Dict):
    return lambda: DictonaryObfuscator(name = args["name"], path = args["path"])

class DictonaryObfuscator(Obfuscator):
    """
    Dictonary should be string --> emoji
    """
    def __init__(self, name: str = "DictonaryObfuscator", path: str = None) -> Self:
        self._logger = getLogger("__main__")
        if path:
            self.load_dictionary(path)
        super().__init__(name)

    def load_dictionary(self, path: str):
        with open(path, 'r', encoding='utf-8') as file:
            self._dictionary_used: dict = json.load(file)

        reversed_dict = {v:k for k,v in self._dictionary_used.items()}
        self._dictionary_used = {v:k for k,v in reversed_dict.items()}   

    def obfuscate(self, user_prompt: Dict) -> str:
        if hasattr(self, "_dictionary_used"):
            return smart_replace(user_prompt["original_prompt"], self._dictionary_used)
        reversed_dict = {v:k for k,v in user_prompt["obfuscated_dictonary"].items()}
        self._dictionary_used = {v:k for k,v in reversed_dict.items()}                       ## These two lines are to insure values are unique
        return smart_replace(user_prompt["original_prompt"], self._dictionary_used)

    def deobfuscate(self, obfuscated_answer: str) -> str:
        return smart_replace(obfuscated_answer, {v:k for k,v in self._dictionary_used.items()})
