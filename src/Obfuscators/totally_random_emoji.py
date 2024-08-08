import sys
import os
import re
from random import random, randrange
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.azure_client import get_answer

prompt = "change a few of the words in the following text with random emojis + \n" 
random_emojis = """
🐋🐍🎺🐊🎨🦀🐩🦉🎬🦏🐦🐗🐼🎸🐃🐌🐱🦅🐡🐑🐰🎭🦉🎷🎲🐝🎸🦀🎥🐜🦄🎮🎃🐢🐻🎮🎲🎮🐰🐺🎮🐹🎧🎺🎮🦄🎨🐭🎸🐠🐨🐛🦐🐟🐦🎤🎲🐼🦀🐭🐬🐾🐒🎥🐰🦀🐭🐡🐢🐿🐋🐿🐨🐻🐱🎈🦊🐣🎃🦁🐂🎧🎃🎥🐶🐍🎲🐮🎤🐘🎨🎸🐰🎭🎤🐧🎸🦄🦇🦎🐺🎥🐭🎷🦁🐦🎃🎶🐢🎹🦋🎮🦀🎤🐸🎷🐠🎶🎲🐦🎨
"""
class TotallyRandomEmoji(Obfuscator):
    def __init__(self):
        self.dict = {}


    def obfuscate(self, user_prompt):
        words_list = re.split(r'\b', user_prompt)
        words_list = sorted(words_list, key=len, reverse=True)
        random_dict = {}
        obfuscated_prompt = user_prompt
        for word in set(words_list):
            if random() < 0.15:
                x = randrange(0, len(random_emojis)-4)
                y = randrange(1, 4)
                random_dict[word] = random_emojis[x:x+y]
                obfuscated_prompt = obfuscated_prompt.replace(word, random_dict[word])

        self.dict = random_dict
        return obfuscated_prompt

    def deobfuscate(self, obfuscated_answer):
        deobfuscated_answer = obfuscated_answer
        sorted_dictonary_list = list(self.dict.items())
        sorted_dictonary_list.sort(key = lambda x: len(x[1]), reverse=True)
        for word, emoji in sorted_dictonary_list:
            deobfuscated_answer = deobfuscated_answer.replace(emoji, word)
        return deobfuscated_answer
    