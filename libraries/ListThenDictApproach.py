import ollama
import string
import re
import os
import logging

import AnswerExtraction
import my_logging

from abstract_client import OllamaClient

class OllamaClient:
    def __init__ (self, name, log_path):
        self.name = name
        self.log_path = log_path
        self.client = ollama.Client(host='http://172.23.81.3:11434')
        self.log = my_logging.init_logs(log_path,name)
        self.prompt_list =[]
        self.chat_history =[]
        self.log.info(
            f"Created OllamaClient {self.name}\n"
        )
    
    def update_chat_history(self, role, content):
        self.chat_history.append({
        'role': role,
        'content': content,
    })

    def set_encryption_prompt(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.read().splitlines()
            prompt = ""
            for line in lines:
                if line == "________________________________________________________________":
                    self.prompt_list.append(prompt)
                    prompt = ""
                    continue
                prompt += line + '\n'
        self.log.info(
        f"{self.name} Updated self.prompt_list:\n{self.prompt_list}\n"
        )

    def send_query(self,model,text,prompt_number):
        self.update_chat_history(self,'user',self.prompt_list[prompt_number].format(text=text))
        answer_for_list_of_words = self.client.chat(model = model, messages = self.prompt_list[0].format(text=text))
        self.update_chat_history(self,'assistant',answer_for_list_of_words["message"])
        return answer_for_list_of_words

    def get_encryption_dict(self, model, text):
        self.chat_history = []
        extracted_answer_for_list_of_words = AnswerExtraction.extract_list(self.send_querry(self,model,text,0))
        extracted_answer_for_list_of_key_words = AnswerExtraction.extract_list(self.send_querry(self,model,text,1))
        extracted_dict = AnswerExtraction.extract_dict(self.send_querry(self,model,text,2))
        self.log.info(
    f"""
List of words
{extracted_answer_for_list_of_words}
List of key words
{extracted_answer_for_list_of_key_words}
Encryption dict:
{extracted_dict}
Chat history:
{self.chat_history}
"""
            )
        self.dict = extracted_dict
        return extracted_dict


    def get_encryption_text(self,text):
        words_in_text = text.split()  # Split the text into words
        total_words = len(words_in_text)  # Count the total number of words
        encrypted_text = text
        words_replaced = 0  # Initialize the counter to zero

        for key in self.dict.keys():
            if len(self.dict[key])<1 or len(key)<1:
                continue
            if key in encrypted_text:
                count = text.count(key)  # Count occurrences of the key in the text
                encrypted_text = encrypted_text.replace(key, self.dict[key])
                words_replaced += count  # Increment the counter by the number of replacements made
        
        if total_words > 0:  # To avoid division by zero
            percentage_words_replaced = (words_replaced / total_words)*100
        else:
            percentage_words_replaced = 0  # If the text is empty, set percentage to zero

        return encrypted_text, percentage_words_replaced


    def get_decryption_text(self,encrypted_text):
        decrypted_text = encrypted_text
        for key in self.dict.keys():
            if len(self.dict[key])<1 or len(key)<1:
                continue
            decrypted_text = decrypted_text.replace(self.dict[key],key)
        return decrypted_text
    
