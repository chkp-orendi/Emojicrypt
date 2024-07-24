import ollama
import sys
import os

import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libraries')))
from ollama_helper import OllamaHelper

if __name__ == "__main__":
    client = OllamaHelper("llama3:8b", "../", "llama3:8b")  
    print(client.send_query("hi"))

    