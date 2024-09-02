import json
import os
import sys
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.utils.azure_client import get_answer, get_embedding



def load_json_from_gpt(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

def fix_answer(data):
    new_data = []
    for case in data["prompts"]:
        new_data.append({
            "prompt": case["paragraph"]
        })
    return new_data

def save_json(data,path):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def json_paragraph_to_data_set(data):
    new_data = []
    for index, case in enumerate(data["prompts"]):
        print(index)
        new_case = {
            "original_prompt": get_answer(case["paragraph"])
        }
        new_case["original_answer"] = get_answer(new_case["original_prompt"])
        new_case["original_prompt_embedding"] = get_embedding(new_case["original_prompt"])
        new_case["original_answer_embedding"] = get_embedding(new_case["original_answer"])
        new_data.append(new_case)
    return new_data

def main():
    input_path = os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024","01", "finance_data_set_18_54.json")
    data = load_json_from_gpt(input_path)                                 # Note: the answer most time will be string and not json. print it and copy paste to the file and fix it manually
    new_data = json_paragraph_to_data_set(data)

    output_path = os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024","01", "finance_data_set.json")
    save_json(new_data,output_path)

if __name__ == "__main__":
    main()