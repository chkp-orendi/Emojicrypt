import ollama


class OllamaHelper:
    def __init__ (self, name, log_path, model, tempurature):
        self._name = name
        self._model = model
        self._log_path = log_path
        self._client = ollama.Client(host='http://172.23.81.3:11434')
        self._prompt_list =[]
        self._chat_history =[]
        self._tempurature = tempurature

    def update_chat_history(self, role, content):
        self._chat_history.append({
        'role': role,
        'content': content,
    })

    def send_query(self, text):
        self.update_chat_history('user', text)
        llm_response = self._client.chat(model=self._model, messages=self._chat_history,options={"temperature": self._tempurature, "max_tokens": 400})
        self.update_chat_history('assistant', llm_response["message"]["content"])
        return llm_response["message"]["content"]

    def get_history(self):
        return self._chat_history