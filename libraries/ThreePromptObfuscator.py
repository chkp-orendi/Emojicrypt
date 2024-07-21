from ollama_helper import OllamaHelper

class ThreePromptsObfuscator:
    def __init__(self, find_sensitive_prompt, find_crucial_prompt, replace_prompt, llm_wrapper):
        self.find_sensitive_prompt = find_sensitive_prompt
        self.find_crucial_prompt = find_crucial_prompt
        self.replace_prompt = replace_prompt
        self.llm_wrapper = llm_wrapper

    def _extract_sensitive(self, user_prompt):
        response_text = self.llm_wrapper.send_query(self.find_sensitive_prompt.format(text=user_prompt))
        return self.llm_tokenize(response_text)

    def _find_crucial(self, user_prompt):
        response_text = self.llm_wrapper.send_query(self.find_sensitive_prompt.format(text=user_prompt))
        return self.llm_tokenize(response_text)

    def _replace(self, text, sensitive, crucial):
        response_text = self.llm_wrapper.send_query(self.replace_prompt.format(text=text, sensitive=sensitive, crucial=crucial))
        #TODO: how should we format the sensitives?
        return response_text

    def obfuscate(self, user_prompt):
        extracted_sensitive = self._extract_sensitive(user_prompt)
        extracted_crucial = self._find_crucial(user_prompt)
        response_text = self._replace(text=user_prompt, sensitive=extracted_sensitive, crucial=extracted_crucial)
