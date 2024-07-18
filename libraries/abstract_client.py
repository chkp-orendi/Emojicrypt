import ollama
import string
import re
import os
import logging
import sys

script_dir = os.path.dirname(__file__)  
parent_dir = os.path.dirname(script_dir)  
target_dir = os.path.join(parent_dir, 'libraries') 
sys.path.append(target_dir)

import AnswerExtraction
import my_logging

class OllamaClient:
    def __init__ (self, name, log_path):
        pass
    
    def set_encryption_prompt(self, file_path):
        pass

    def get_encryption_dict(self):
        pass

    def get_encryption_text(self):
        pass

    def get_decryption_text(self):
        pass

    def update_chat_history(self, role, content):
        pass

    def write_to_log(self):
        pass
