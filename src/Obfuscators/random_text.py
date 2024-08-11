import sys
import os
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator

class RandomText(Obfuscator):
    def __init__(self, llm_wrapper_factory, logger):
        self._client = llm_wrapper_factory
        self._logger = logger


    def obfuscate(self, user_prompt):
        return self._client.get_answer(f"generate a random text with {len(user_prompt["original_question"])} characters")

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer
