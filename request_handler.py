import sys
import re
from typing import Dict
import re
import sys
import os
import json
import datetime
import ast

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import time

tokenizer = AutoTokenizer.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection-v2")
model = AutoModelForSequenceClassification.from_pretrained("ProtectAI/deberta-v3-base-prompt-injection-v2")

classifier = pipeline(
  "text-classification",
  model=model,
  tokenizer=tokenizer,
  truncation=True,
  max_length=512,
  device=torch.device("cpu"),
)


from src.utils.string_utils import smart_replace
from src.utils.azure_client import AzureClient
from src.utils.ollama_client import OllamaClient
from src.Obfuscators.phase_1_obfuscator import PhaseOneObfuscator
"""
This is a prototype obfuscator I will pass to the GW to see how it works.
"""

azure_llm_wrapper_factory = lambda :AzureClient("azure_client",  "../", "gpt-4o-2024-05-13", 0.0)
ollama_llm_wrapper_factory = lambda :OllamaClient("llama3:8b", "../", "llama3:8b", 0.0)
obfuscator_prefix = "Do not explain the emojis in your answer and other than the exact emoji sequences from the original prompt, do not use emojis in your answer."

obfuscator = PhaseOneObfuscator(name = "prototype", llm_wrapper_factory=ollama_llm_wrapper_factory, prompt_prefix=obfuscator_prefix, lower_bound_percentage = 75, upper_bound_percentage = 95)

def precentage_of_changed_word_obfuscating(original_text: str, dictionary_used: dict):
    """
    Get precentage of changed words in the text.
    Dictionary is text to emoji mapping.
    """
    copy_text = original_text.lower()
    number_of_words = len(original_text.split())
    count = 0
    for key in sorted(dictionary_used.keys()):              
        matches = re.findall(rf'\b{re.escape(key.lower())}\b', copy_text)
        print(key, matches)
        if matches:
            copy_text = smart_replace(copy_text, {key.lower(): ""})
            count += len(matches) * len(key.split())
    return count/number_of_words

def main():
    start_time = datetime.datetime.now()

    pattern = r'(.*"parts":\[")([\s\S]*?)("\]},"metada.*)'

    with open('/home/admin/Emojicrypt/input.txt', 'r') as file:
        request_body = file.read()

    print("request_body: ", request_body)
    matches = re.search(pattern, request_body)
    if matches:
        prompt = matches.group(2)
        prefix = matches.group(1)
        suffix = matches.group(3)
        print("prompt: ", prompt)

        result = classifier(prompt)
        print(result)

        # if result[0]["label"] == "INJECTION" and result[0]["score"] >0.98:
        #     """prefix + obfuscated_prompt + suffix"""
        #     prefix = ""
        #     suffix = ""
        #     obfuscated_prompt = "<ADD HERE JSON WITH PROMPT INJECTION DETECTED>" #TODO
        #     dict = {}
            
        elif len(prompt) <150:
            obfuscated_prompt = request_body
            prefix = ""
            suffix = ""
            dict = {}
        else:
            obfuscated_prompt, time_dictionary = obfuscator.obfuscate_with_time({"original_prompt": prompt})
            obfuscated_prompt = obfuscated_prompt.strip('"')
            print("obfuscated: ", obfuscated_prompt)
            dict = obfuscator.get_dictionary()
            # print("dictionary: ", dict)
    else:
        print("did not find pattern")
        obfuscated_prompt = request_body
        prompt = "No prompt found"
        prefix = ""
        suffix = ""
        dict = {}
    
    with open('/home/admin/Emojicrypt/original_prompt.txt', 'w', encoding='utf-8') as file:
        file.write(prompt)
        file.flush()
    try:    
        with open('/home/admin/Emojicrypt/encryption_dictonary.json', 'r') as file:
            old_dictionary = json.load(file)
            new_dict = {**old_dictionary, **dict}
    except FileNotFoundError:
        print("creating new encryption_dictionary.json")
        new_dict = dict


    with open('/home/admin/Emojicrypt/encryption_dictonary.json', 'w', encoding='utf-8') as file:
        json.dump(new_dict, file, ensure_ascii=False, indent=4)


    with open('/home/admin/Emojicrypt/output.txt', 'w') as file:
        file.write("MAGIC" + prefix + obfuscated_prompt + suffix)
        file.flush()
    
    end_time = datetime.datetime.now()
    perc_words_changed = 0
    if (prefix != ""):
        prefix_len = len("Do not explain the emojis in your answer and other than the exact emoji sequences from the original prompt, do not use emojis in your answer.")
        perc_words_changed = precentage_of_changed_word_obfuscating(prompt[prefix_len:], new_dict)
        
    with open('/home/admin/Emojicrypt/info.txt', 'a+', encoding = 'utf-8') as file:
        file.write("\n___________________________________________________________________________REQUEST_______________________________________________________________________________________________________\n")
        file.write(prompt+"\n")
        file.write("_________________________________________________________________________________________________________________________________________________________________________________________\n")
        file.write(obfuscated_prompt+"\n")
        file.write("_________________________________________________________________________________________________________________________________________________________________________________________\n")
        file.write(str(dict)+"\n")
        file.write("_________________________________________________________________________________________________________________________________________________________________________________________\n")
        file.write(f"percentage of words changed: {perc_words_changed}\n")
        file.write("_________________________________________________________________________________________________________________________________________________________________________________________\n")
        if prefix == "":
            file.write(f"total time: {end_time-start_time}\n")
        else:
            file.write(f"""get dictionary terms: {time_dictionary["get dictionary terms"]}
get terms obfuscation: {time_dictionary["get terms obfuscation"]}
total time: {end_time-start_time}
""")
        file.flush()

if __name__ == '__main__':
    print("starting\n")
    main()

