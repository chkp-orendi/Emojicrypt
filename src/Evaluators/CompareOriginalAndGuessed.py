import json
import os
import sys
import numpy as np

from  dotenv import load_dotenv
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.utils.azure_client import get_answer
from src.utils.string_utils import smart_replace, extract_answer



def get_dictionary(dictionary_str : str):
    dictionary = {}
    for line in dictionary_str.split('\n')[1:-1]:
        try:
            key, value = line.split(':')        # This order  is to insure dictionary: string -> emoji (smart_replace needs s->e)
            key = key.strip(' ",\\')
            value = value.strip(' ",\\')
            dictionary[key] = value       
        except Exception as e:
            print("error")
            print(e, line)

    return dictionary


def compare_original_and_guessed(case: dict) -> float:

    prompt = """Given the following two text, give a number between 0.0 to 1.0 how similar you think the meaning of the two texts are.
Text1: {text1}
Text2: {text2}
Write $ANSWER: <number> in your answer"""



    obfuscation_dict = get_dictionary(case["llm_gussed_answer"])

    dycrpyted_obfuscated_answer = smart_replace(case["obfuscated_prompt"], obfuscation_dict)

    answer_1 = get_answer(prompt.format(text1=case["original_answer"], text2=dycrpyted_obfuscated_answer))
    answer_2 = get_answer(prompt.format(text2=case["original_answer"], text1=dycrpyted_obfuscated_answer))
    answers = [answer_1, answer_2]
    extracted_answers = [extract_answer(answer) for answer in answers]
    average = 0.0
    for number in extracted_answers:
        count = 1
        if number != None:
            average += float(number)
            count += 1
    return answers, average/count
    

def load_data(path) -> json:
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_data(data, path):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False ,indent=4)

def main():
    # Movies
    data = load_data(os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024", os.getenv("DATE"), "json obfuscator test2024-09-05_13_44_01.350967.json"))
    for obfuscator in data:
        for index, case in enumerate(obfuscator[1]):
            print(index)
            answers, score = compare_original_and_guessed(case)
            case["score for decryption attemp"] = score
            case["answers for dycrypted try"] = answers

    save_data(data, os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024", os.getenv("DATE"), "Presentation" "Movie Result.json"))
    
    # Finance
    # data = load_data(os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024","2024-09-04","Presentation", "Original Finance Results.json"))
    # for obfuscator in data:
    #     if obfuscator[0] == "SmartRandom":
    #         continue
    #     for index, case in enumerate(obfuscator[1]):
    #         print(index)
    #         answers, score = compare_original_and_guessed(case)
    #         case["score for dycrypted try"] = score
    #         case["answers for dycrypted try"] = answers

    # save_data(data, os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024","2024-09-04","Presentation", "Original Finance  Results_2.json"))

if __name__ == "__main__":
    main()
