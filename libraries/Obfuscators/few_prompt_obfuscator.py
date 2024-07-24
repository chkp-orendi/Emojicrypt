import re
from obfuscator_template import Obfuscator


#Convention that last prompt would return $Dict [key1:value1,key2:value2,...]

class FewPromptsObfuscator(Obfuscator):
    def __init__(self, prompt_list, llm_wrapper_factory, logger):
        self._prompt_list = prompt_list
        self._llm_wrapper_factory = llm_wrapper_factory
        self._logger = logger
        self._dictionary_used = {}

    @staticmethod
    def extract_list(LLM_answer):
        ANSWER_PATTERN = r'\[([^\]]+)\]'
        answer_list = re.findall(ANSWER_PATTERN, LLM_answer)
        if len(answer_list) >= 1:
            answer_list = answer_list[-1]  # return last occurrence of pattern.
        else:
            return []

        return [token.strip("' \t") for token in answer_list.split(',')]

    @staticmethod
    def extract_dict(LLM_answer):
        ANSWER_PATTERN = r'\$Dict:\s*\[(?:\s*[^:\[\],]+:[^:\[\],]+\s*,)*\s*[^:\[\],]+:[^:\[\],]+\s*\]'
        answer_list = re.findall(ANSWER_PATTERN, LLM_answer)
        if len(answer_list) >= 1:
            answer_list = answer_list[-1]  # return last occurrence of pattern.
        else:
            return {}
        words_replacements = {}
        answer_list = answer_list.replace("$Dict:", "").strip("[] \"")
        print(answer_list)
        for item in answer_list.split(","):
            splited_item = item.split(":")
            if len(splited_item) !=2:
                print("INVALID ITEM")
                print(item)
                print(LLM_answer)
                continue
            words_replacements[item.split(":")[0].strip("' \t")] = item.split(":")[1].strip("' \t")
        return words_replacements

    
    def obfuscate(self, user_prompt):
        self._llm_wrapper = self._llm_wrapper_factory()
        
        first_iteration = True
        for prompt in self._prompt_list:
            if first_iteration:
                llm_answer = self._llm_wrapper.send_query(prompt.format(text=user_prompt))
                self._logger.info("First answer:" )
                first_iteration = False
            else:
                llm_answer = self._llm_wrapper.send_query(prompt)
                self._logger.info("Following answers:" )
            
            self._logger.info(llm_answer)
                
        self._dictionary_used = FewPromptsObfuscator.extract_dict(llm_answer)
        if len(self._dictionary_used) == 0:
            self._logger.info("Empty dictionary_used")
            print("Empty dictionary_used")
        else:
            self._logger.info("dictionary_used:" + str(self._dictionary_used))
            print("dictionary_used:" + str(self._dictionary_used))

        response_text = user_prompt
        for key, value in self._dictionary_used.items():
            response_text = re.sub(r'\b' + re.escape(key) + r'\b', value, response_text)
        return response_text

    def deobfuscate(self, obfuscated_answer):
        deobfuscated_answer = obfuscated_answer
        for key, value in self._dictionary_used.items():
            deobfuscated_answer = re.sub(r'\b' + re.escape(value) + r'\b', key, deobfuscated_answer)
        return deobfuscated_answer
