import re

from obfuscator_template import Obfuscator

class ThreePromptsObfuscator(Obfuscator):
    def __init__(self, extract_terms_prompt, find_crucial_prompt, dictionary_prompt, llm_wrapper_factory, logger):
        self._extract_terms_prompt = extract_terms_prompt
        self._find_crucial_prompt = find_crucial_prompt
        self._dictionary_prompt = dictionary_prompt
        self._llm_wrapper_factory = llm_wrapper_factory
        self._extracted_terms = []
        self._extracted_crucial = {}
        self._dictionary_used = {}
        self._logger = logger

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
        ANSWER_PATTERN = r'\[([^\]]+)\]'
        answer_list = re.findall(ANSWER_PATTERN, LLM_answer)
        if len(answer_list) >= 1:
            answer_list = answer_list[-1]  # return last occurrence of pattern.
        else:
            return {}
        words_replacements = {}
        for item in answer_list.split(","):
            splited_item = item.split(":")
            if len(splited_item) !=2:
                print("INVALID ITEM")
                print(item)
                print(LLM_answer)
                continue
            words_replacements[item.split(":")[0].strip("' \t")] = item.split(":")[1].strip("' \t")
        return words_replacements
        #return {item.split(":")[0]: item.split(":")[1] for item in answer_list}

    def _extract_terms(self, user_prompt):       
        response_text = self._llm_wrapper.send_query(self._extract_terms_prompt.format(text=user_prompt))
        return ThreePromptsObfuscator.extract_list(response_text)

    def _find_crucial(self, user_prompt):
        response_text = self._llm_wrapper.send_query(self._find_crucial_prompt.format(text=user_prompt))
        self._logger.info("Crucial:" )
        self._logger.info(response_text)
        return set(ThreePromptsObfuscator.extract_list(response_text))

    def _find_replacements(self, text, from_list):
        response_text = self._llm_wrapper.send_query(self._dictionary_prompt.format(text=text, words_list=from_list))
        return ThreePromptsObfuscator.extract_dict(response_text)

    def obfuscate(self, user_prompt):
        self._llm_wrapper = self._llm_wrapper_factory()
        self._extracted_terms = self._extract_terms(user_prompt)
        self._extracted_crucial = self._find_crucial(user_prompt)
        self._extracted_terms = [item for item in self._extracted_terms if item not in self._extracted_crucial]
        self._dictionary_used = self._find_replacements(text=user_prompt, from_list=self._extracted_terms)
        if len(self._dictionary_used) == 0:
            self._logger.info("Empty dictionary_used")
        else:
            self._logger.info("dictionary_used:" + str(self._dictionary_used))

        response_text = user_prompt
        for key, value in self._dictionary_used.items():
            response_text = re.sub(r'\b' + re.escape(key) + r'\b', value, response_text)
        return response_text

    def deobfuscate(self, obfuscated_answer):
        deobfuscated_answer = obfuscated_answer
        for key, value in self._dictionary_used.items():
            deobfuscated_answer = re.sub(r'\b' + re.escape(value) + r'\b', key, deobfuscated_answer)
        return deobfuscated_answer
