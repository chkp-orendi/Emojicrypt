import sys
import os
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator

class FakeObfuscator(Obfuscator):
    def __init__(self):
        pass


    def obfuscate(self, user_prompt):
        return user_prompt["original_question"]

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer
