import ollama
import string
import re
import os
import logging

import AnswerExtraction
import my_logging

class OllamaClient:
    def __init__ (self, name, log_path):
        self.name = name
        self.log_path = log_path
        self.client = ollama.Client(host='http://172.23.81.3:11434')
        self.log = my_logging.init_logs(log_path,name)
    
    def load_encryption_prompt(self, file_path):
        self.prompts = []



log_path = '~/Emoji/Emojicrypt/log/wrong_format_encryption.log'
def init_Ollama_client():
    client = ollama.Client(host='http://172.23.81.3:11434')
    return client

chat_history = []

def get_list_of_intresting_words(text, client ,model='llama3:8b'):
    text_prompt =f"""can you identify all of the words in the context that can be defined as: technical terms, acronyms, corporate lingo. List these words in the following format: $LIST [word1, word2, ..., wordN].
Here is an exampl:
Context: The board of directors at Acme Corp has recently expanded from 8 to 12 members to increase diversity.
How many new members were added to the board of Acme Corp?
Answer: $LIST [diversity, board of directors, Corp]
    
Now give me a list for this Context: {text}"""
    chat_history.append({
        'role': 'user',
        'content': text_prompt,
    })
    answer = client.generate(model = model, prompt = text_prompt)
    chat_history.append({
        'role': 'assistant',
        'content': answer["response"],
    })
    print("$get_list_of_intresting_words")
    print(answer["response"])
    return AnswerExtraction.extract_list(answer["response"])
    
def get_list_of_key_words(text, client ,model='llama3:8b'):
    text_prompt =f"""in addition, can you specify which of the words in the list are required to effectively answer the question?
List these words in the following format: $LIST [word1, word2, ..., wordN]

For the last example you will return: $LIST [board of directors, Corp]
"""
    chat_history.append({
        'role': 'user',
        'content': text_prompt,
    })
    answer = client.chat(model = model, messages = chat_history) 
    chat_history.append({
        'role': 'assistant',
        'content': answer["message"],
    })
    print("$get_list_of_key_words")
    print(answer["message"]["content"])
    return AnswerExtraction.extract_list(answer["message"]["content"])

def get_encryption_dict(text,words_list, client ,model='llama3:8b'):
    text_prompt =f"""For the words in the list: {words_list} find replacement emoji sequence while keeping the original intent. At the end return: $Dict""" + "{word1:emoji1,word2:emoji2,...,wordN:emojiN}"
    text_prompt += """For the last example you would return: $Dict{diversity:👩🏼‍🤝‍👨🏿🌍🌈⚧️}"""
    chat_history.append({
        'role': 'user',
        'content': text_prompt,
    })
    answer = client.chat(model = model,messages=chat_history)
    chat_history.append({
        'role': 'assistant',
        'content': answer["message"],
    })
    print("$get_encryption_dict")
    print(answer["message"]["content"])
    print("$chat_history")
    print(chat_history)
    return AnswerExtraction.extract_dict(answer["message"]["content"])

def get_encryption_dict(text, client ,model='llama3:8b'):
    # enc_logger = logging.getLogger('wrong format encryption')

    chat_history = []
    list_of_words = get_list_of_intresting_words(text, client ,model='llama3:8b')
    list_of_key_words = get_list_of_key_words(text, client ,model='llama3:8b')
    
    words_to_change = list(set(list_of_words)-set(list_of_key_words))
    encryption_dict = get_encryption_dict(text,words_to_change, client ,model='llama3:8b')
    
    return encryption_dict

def get_encryption_text(text, encryption_dict):
    words_in_text = text.split()  # Split the text into words
    total_words = len(words_in_text)  # Count the total number of words
    encrypted_text = text
    words_replaced = 0  # Initialize the counter to zero

    for key in encryption_dict.keys():
        if len(encryption_dict[key])<1 or len(key)<1:
            continue
        if key in encrypted_text:
            count = text.count(key)  # Count occurrences of the key in the text
            encrypted_text = encrypted_text.replace(key, encryption_dict[key])
            words_replaced += count  # Increment the counter by the number of replacements made
    
    if total_words > 0:  # To avoid division by zero
        percentage_words_replaced = (words_replaced / total_words)*100
    else:
        percentage_words_replaced = 0  # If the text is empty, set percentage to zero

    return encrypted_text, percentage_words_replaced


def get_decryption_text(encrypted_text, encryption_dict):
    decrypted_text = encrypted_text
    for key in encryption_dict.keys():
        if len(encryption_dict[key])<1 or len(key)<1:
            continue
        decrypted_text = decrypted_text.replace(encryption_dict[key],key)
    return decrypted_text
