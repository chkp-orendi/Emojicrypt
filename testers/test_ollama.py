import ollama
import sys
import os
import re
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libraries')))
from ollama_helper import OllamaHelper
import AzureApi

def obfuscate(user_prompt,dict):
    encrypted_text = user_prompt 
    for original, obfuscated in dict.items():
        #encrypted_text = encrypted_text.replace(original, obfuscated)
        encrypted_text = re.sub(r'[a-zA-Z0-9.,()?!*$#\s\t\b]' + re.escape(original) + r'[a-zA-Z0-9.,()?!*$#\s\t\b]', obfuscated, user_prompt)
    return encrypted_text 

if __name__ == "__main__":
    # client = OllamaHelper("llama3:8b", "../", "llama3:8b",  0.0)  
    # print(client.send_query("hi"))

    text = "What are the benefits of implementing DevSecOps practices in our software development lifecycle, and how do they help in identifying and mitigating security vulnerabilities early?"

    obfuscated_dictionary = {
                    "DevSecOps": " \ud83d\udee0\ufe0f\ud83d\udd12\ud83d\udd04",
                    " software development lifecycle": " \ud83d\udcbb\ud83d\udd04\ud83d\udcc8",
                    " security vulnerabilities": " \ud83d\udd13"
                }
    obfuscated_text = obfuscate(text, obfuscated_dictionary)
    print(obfuscated_text.encode('utf-8', 'surrogatepass').decode('utf-8', 'surrogateescape'))