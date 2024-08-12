import sys
import os
from dotenv import load_dotenv 
from typing import Dict

load_dotenv()
from logging import Logger, getLogger
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator


# Replace the second part of the prompt with a completely irrelevant text
class WrongObfuscator(Obfuscator):
    def __init__(self, name: str):
        self._logger = getLogger("__main__")
        super().__init__(name)
        

    def obfuscate(self, user_prompt):
        return  "A quick brown fox jumps over a lazy cpdog" + user_prompt["original_question"][int(len(user_prompt)/2):]

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer


def make_wrong_obfuscator(args: Dict):
        return lambda: WrongObfuscator(name = "WrongObfuscator")