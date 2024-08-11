import re
import sys
import os
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.answer_extraction import smart_replace


#Convention that last prompt would return $Dict [key1:value1,key2:value2,...]

class FewPromptsObfuscator(Obfuscator):
    def __init__(self, prompt_list, llm_wrapper_factory, logger, prompt_prefix=""):
        self._prompt_list = prompt_list
        self._llm_wrapper_factory = llm_wrapper_factory
        self._logger = logger
        self._dictionary_used = {}
        self._prompt_prefix = prompt_prefix

    
    def obfuscate(self, user_prompt):
        self._llm_wrapper = self._llm_wrapper_factory()
        
        first_iteration = True
        for prompt in self._prompt_list:
            if first_iteration:
                llm_answer = self._llm_wrapper.send_query(prompt.format(text=user_prompt["original_question"]))
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

        response_text = user_prompt["original_question"]
        response_text = smart_replace(response_text,self._dictionary_used)
        return self._prompt_prefix + response_text

    def deobfuscate(self, obfuscated_answer):
        deobfuscated_answer = obfuscated_answer
        deobfuscated_answer = smart_replace(deobfuscated_answer,{value:key for key,value in self._dictionary_used.items()})
        return deobfuscated_answer
