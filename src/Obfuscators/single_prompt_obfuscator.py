import re

import sys
import os
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator


class SinglePromptObfuscator(Obfuscator):
    def __init__(self, prompt_list, llm_wrapper_factory, logger, prompt_prefix = ""):
        self._prompt = prompt_list[0]
        self._llm_wrapper = llm_wrapper_factory
        self._dictionary_used = {}
        self._logger = logger
        self._prompt_prefix = prompt_prefix


    def _get_encryption_dict(self, llm_query):
        encryption_dict = {}
        answer = self._llm_wrapper().send_query(self._prompt.format(text=llm_query))
        self._logger.info(f"Encryption dictionary raw answer: {answer}")
        model_encryption = re.findall(r'Replacements:*\s*\[([^\]]+)\]',answer)
        if len(model_encryption)>0:
            model_encryption=model_encryption[-1]
        else:
            return {}

        for item in model_encryption[0:-1].split(","):
            try:
                key, value = item.split(";")
                if (len(key)==0) or (len(value)==0):
                    continue
            except:
                try:
                    key, value = item.split(":")
                    if (len(key)==0) or (len(value)==0):
                        continue
                except:
                    continue
            encryption_dict[key]= value
        self._dictionary_used = encryption_dict
        self._logger.info(f"Encryption dictionary: {encryption_dict}")
        return encryption_dict
    
    def obfuscate(self, user_prompt):
        self._get_encryption_dict(user_prompt)
        encrypted_text = user_prompt 
        for original, obfuscated in self._dictionary_used.items():
            encrypted_text = encrypted_text.replace(original, obfuscated)
            #encrypted_text = re.sub(r'\b' + re.escape(original) + r'\b', obfuscated, user_prompt)
        self._logger.info(f"obfuscate: {encrypted_text}")
        return self._prompt_prefix+ encrypted_text 

    def deobfuscate(self, obfuscated_answer):
        decrypted_text = obfuscated_answer 
        for original, obfuscated in self._dictionary_used.items():
            decrypted_text = decrypted_text.replace(obfuscated, original)
            #decrypted_text = re.sub(re.escape(obfuscated), original, decrypted_text)
        self._logger.info(f"obfuscated_answer: {decrypted_text}")
        return decrypted_text
    
