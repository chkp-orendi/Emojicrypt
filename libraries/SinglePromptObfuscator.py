import re


class SinglePromptsObfuscator:
    def __init__(self, prompt, llm_wrapper, logger):
        self._prompt = prompt
        self._llm_wrapper = llm_wrapper
        self._extracted_terms = []
        self._extracted_crucial = {}
        self._dictionary_used = {}
        self._logger = logger

    def _get_encryption_dict(self, llm_query):
        encryption_dict = {}
        answer = self._llm_wrapper.send_query(self._prompt.format(text=llm_query))
        model_encryption = re.findall(r'\{[^{}]*\}',answer["response"])
        if len(model_encryption)>1:
            model_encryption=model_encryption[1]
        else:
            model_encryption =model_encryption[0]
        if (len(model_encryption)<3):
            return "NO VALID ANSWER"
        for item in model_encryption[1:-1].split(","):
            try:
                key, value = item.split(";")
            except:
                try:
                    key, value = item.split(":")
                except:
                    return "NO VALID ANSWER"
            encryption_dict[key]=value
        self._encryption_dict = encryption_dict
        self._logger.info(f"Encryption dictionary: {encryption_dict}")
        return encryption_dict
    
    def obfuscate(self, user_prompt):
        encryption_dict = self._encryption_dict(user_prompt)
        encrypted_text = user_prompt 
        for key in encryption_dict.keys():
            encrypted_text = encrypted_text.replace(key,encryption_dict[key])
        self._logger.info(f"obfuscate: {encrypted_text}")
        return encrypted_text 

    def deobfuscate(self, obfuscated_answer):
        decrypted_text = obfuscated_answer 
        for key in self._encryption_dict.keys():
            decrypted_text = decrypted_text.replace(self._encryption_dict[key],key)
        self._logger.info(f"obfuscated_answer: {decrypted_text}")
        return decrypted_text 