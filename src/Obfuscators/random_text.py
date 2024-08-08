import sys
import os
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.azure_client import get_answer
class RandomText(Obfuscator):
    def __init__(self):
        pass


    def obfuscate(self, user_prompt):
        return get_answer(f"generate a random text with {len(user_prompt)} characters")

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer
