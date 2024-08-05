import glob
import os
import json
import pandas as pd
import re
import sys

from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.utils.ollama_client import OllamaClient
from src.utils.azure_client import AzureClient


def extract_number(text):
    # Use regular expression to find all numbers in the text
    match = re.search(r'\b' + r'\d+' + r'\b', text)
    if match:
        return int(match.group())
    else:
        return None


def new_metric(text1,text2):
    prefix = "give a number between 0-100 where 0 is not similar at all and 100 is the exact same text for the similarity for these 2 texts:"
    answer = AzureClient.get_answer(prefix + text1 + text2, model="gpt-4o-2024-05-13", temp=0.0)
    #client = ollama_helper.OllamaHelper("llama3:8b", "../", "llama3:8b", 0.0)
    #answer = client.send_query(prefix + text1 + text2, client)
    #client._chat_history = []
    answer_number = extract_number(answer)
    return answer_number

def convert_json(name, data, new_metric):

    new_json = []

    for obfuscator in data:
        qindex = 0
        obfuscator_name = obfuscator[0]
        obfuscator_data = obfuscator[1]
        obfuscator_data_with_new_metric = []
        for obfuscator_values in obfuscator_data:
            # if len(obfuscator_values) <= 1:
            #     continue
            original_answer = obfuscator_values['original_answer']
            original_prompt = obfuscator_values['original_prompt']
            obfuscated_prompt = obfuscator_values['obfuscated_prompt']
            obfuscated_answer = obfuscator_values['deobfuscated_answer']
            deobfuscated_answer = obfuscator_values['deobfuscated_answer']
            prompt_metric = new_metric(original_prompt,obfuscated_prompt)
            answer_metric = new_metric(original_answer,obfuscated_answer)
            obfuscated_dictonary = obfuscator_values['obfuscated_dictonary']
            new_data_element = {
                "original_answer": original_answer,
                "original_prompt": original_prompt,
                "obfuscated_prompt": obfuscated_prompt,
                "obfuscated_answer": obfuscated_answer,
                "deobfuscated_answer": deobfuscated_answer,
                "prompt_metric": prompt_metric,
                "answer_metric": answer_metric, 
                "obfuscated_dictonary": obfuscated_dictonary
            }
            obfuscator_data_with_new_metric.append(new_data_element)
            qindex += 1
            if (qindex >20):
                break

        new_json.append([obfuscator_name, obfuscator_data_with_new_metric])

    output_path =os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "metrics", "30-7-Test-Result", "azure_metric", name + ".json")
    with open(output_path, 'w') as file:
            json.dump(new_json, file, indent=4)

if __name__ == "__main__":
    
    data_folder_path = "C:\\Users\\orendi\\Documents\\EmojiCrypt-main\\Emojicrypt\\testers\\metrics\\30-7-Test-Result\\embedding_metric\\2024-07-30_13_04_48.818839-metrics-gpt.json"
    
    # Get all JSON files in the data_path directory
    #json_files = glob.glob(os.path.join(data_folder_path, "*.json"))
    
    #for json_file in json_files:
    for i in range (5):
        with open(data_folder_path, 'r') as file:
            data = json.load(file)
            convert_json("gpt-metric-" + str(i), data, new_metric)
         