import ollama


class OllamaHelper:
    def __init__ (self, name, log_path, model):
        self.name = name
        self.model = model
        self.log_path = log_path
        self.client = ollama.Client(host='http://172.23.81.3:11434')
        self.prompt_list =[]
        self.chat_history =[]

    def update_chat_history(self, role, content):
        self.chat_history.append({
        'role': role,
        'content': content,
    })

    def send_query(self, text):
        self.update_chat_history('user', text)
        llm_response = self.client.chat(model=self.model, messages=self.chat_history,options={"temperature": 0})
        self.update_chat_history('assistant', llm_response["message"]["content"])
        return llm_response["message"]["content"]
