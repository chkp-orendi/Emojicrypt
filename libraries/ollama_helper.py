import ollama
import string
import re
import os
#import logging

import AnswerExtraction
import my_logging

from abstract_client import OllamaClient

class OllamaHelper:
    def __init__ (self, name, log_path, model):
        self.name = name
        self.model = model
        self.log_path = log_path
        self.client = ollama.Client(host='http://172.23.81.3:11434')
        #self.log = my_logging.init_logs(log_path,name)
        self.prompt_list =[]
        self.chat_history =[]
        #self.log.info(            f"Created OllamaClient {self.name}\n"        )

    def update_chat_history(self, role, content):
        self.chat_history.append({
        'role': role,
        'content': content,
    })

    def send_query(self, text):
        self.update_chat_history('user', text)
        llm_response = self.client.chat(model=self.model, messages=self.chat_history)
        self.update_chat_history('assistant', llm_response["message"]["content"])
        return llm_response["message"]["content"]
