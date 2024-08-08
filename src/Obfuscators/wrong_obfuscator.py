import sys
import os
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator


# Replace the second part of the prompt with a completely irrelevant text
class WrongObfuscator(Obfuscator):
    def __init__(self):
        pass

    def obfuscate(self, user_prompt):
        return  "A quick brown fox jumps over a lazy cpdog" + user_prompt["original_question"][int(len(user_prompt)/2):]

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer
