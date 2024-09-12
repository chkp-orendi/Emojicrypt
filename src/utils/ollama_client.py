import ollama
import sys
import os
from typing import Self
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

class OllamaClient:
    def __init__ (self: Self, name: str, log_path: str, model: str, temperature: float):
        self._name = name
        self._model = model
        self._log_path = log_path
        self._client = ollama.Client(host=os.getenv('OLLAMA_SERVER'))
        self._prompt_list =[]
        self._chat_history =[]
        self._temperature = temperature

    def update_chat_history(self, role, content):
        self._chat_history.append({
        'role': role,
        'content': content,
    })

    def send_query(self: Self, text: str, max_tokens= os.getenv("MAX_TOKENS")) -> str :
        self.update_chat_history('user', text)
        llm_response = self._client.chat(model=self._model, messages=self._chat_history,options={"temperature": self._temperature, "max_tokens": max_tokens})
        self.update_chat_history('assistant', llm_response["message"]["content"])
        return llm_response["message"]["content"]

    def get_history(self: Self):
        return self._chat_history
    

# client = OllamaClient("llama3:8b", "../", "llama3:8b", 0.0)
# print(client.send_query("hello"))