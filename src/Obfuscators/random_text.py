import sys
import os
from dotenv import load_dotenv 
from logging import Logger, getLogger
from typing import Self
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator

def make_random_text(args):
    return lambda: RandomText(name = args["name"],
                              llm_wrapper_factory=args["llm_wrapper_factory"])

class RandomText(Obfuscator):
    def __init__(self, name:str , llm_wrapper_factory) -> Self:
        self._llm_wrapper_factory = llm_wrapper_factory
        self._logger = getLogger("__main__")
        super().__init__(name)

    def obfuscate(self, user_prompt):
        self._llm_wrapper = self._llm_wrapper_factory()
        return self._llm_wrapper.send_query(f"generate a random text with {len(user_prompt["original_prompt"])} characters")

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer
