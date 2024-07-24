import re

## Problem with llm_wrapper. We use it for all scnearios in a dataset but for each case it should have a fresh chat history.
## One reason, We want to test for different scenarios.
## Second reason, We can't have chat histroy to long, it will crush


class SinglePromptObfuscator(Obfuscator):
    def __init__(self, prompt, llm_wrapper_factory, logger):
        self._prompt = prompt
        self._llm_wrapper = llm_wrapper_factory
        self._dictionary_used = {}
        self._logger = logger
        


    def _get_encryption_dict(self, llm_query):
        encryption_dict = {}
        answer = self._llm_wrapper().send_query(self._prompt.format(text=llm_query))
        self._logger.info(f"Encryption dictionary raw answer: {answer}")
        model_encryption = re.findall(r'\[([^\]]+)\]',answer)
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
            encrypted_text = re.sub(r'\b' + re.escape(original) + r'\b', obfuscated, user_prompt)
        self._logger.info(f"obfuscate: {encrypted_text}")
        return encrypted_text 

    def deobfuscate(self, obfuscated_answer):
        decrypted_text = obfuscated_answer 
        for original, obfuscated in self._dictionary_used.items():
            decrypted_text = re.sub(r'\b' + re.escape(obfuscated) + r'\b', original, decrypted_text)
        self._logger.info(f"obfuscated_answer: {decrypted_text}")
        return decrypted_text
    