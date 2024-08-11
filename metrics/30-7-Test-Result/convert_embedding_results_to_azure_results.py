import os
import sys
import glob
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Evaluators')))
from gpt_evaluator import GPTEvaluator


prompt_file_name = "emphasis_on_technical_terms.txt"
path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "prompts", "gpt_evaluator" ,prompt_file_name)
evaluator = GPTEvaluator(path)

def convert_data(embedding_data):
    azure_data = []
    for obfuscator in embedding_data:
        obfuscator_name = obfuscator[0]
        i = 0
        obfuscator_test = []
        for prompt in obfuscator[1]:
            print(f"{obfuscator_name} - {i}")
            prompt_dict = {}
            prompt_dict['original_answer'] = prompt['original_answer']
            prompt_dict['original_prompt'] = prompt['original_prompt']
            prompt_dict['obfuscated_prompt'] = prompt['obfuscated_prompt']
            prompt_dict['obfuscated_answer'] = prompt['obfuscated_answer']
            prompt_dict['deobfuscated_answer'] = prompt['deobfuscated_answer']
            prompt_dict['obfuscated_dictonary'] = prompt['obfuscated_dictonary']
            prompt_dict['prompt_metric'] = evaluator.evaluate_prompt(prompt['obfuscated_prompt'], {"scenario": prompt["original_prompt"]})
            prompt_dict['answer_metric'] = evaluator.evaluate_prompt(prompt['deobfuscated_answer'], {"scenario": prompt["original_answer"]})
            obfuscator_test.append(prompt_dict)
            i += 1
        azure_data.append([obfuscator_name, obfuscator_test])
    return azure_data

def save_data(data, output_path):
    with open(output_path, 'w') as file:
        json.dump(data, file,  indent=4)

def main():
    
    data_path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "metrics", "30-7-Test-Result", "embedding_metric")
    files = glob.glob(os.path.join(data_path, "*"))

    for file in files:
        print(os.path.basename(file))
        if os.path.basename(file) == "2024-07-30_11_54_18.347697-metrics-llama.json" or os.path.basename(file) == "2024-07-30_13_04_48.818839-metrics-gpt.json"\
            or os.path.basename(file) == "2024-07-30_14_14_47.797507-metrics-llama-prefix.json" or os.path.basename(file) == "2024-07-30-metrics-WrongAndFake.json":
            continue
        if os.path.isfile(file):
            print(f"Processing file: {file}")

            with open(file, 'r') as f:
                data = json.load(f)

            azure_data = convert_data(data)
            output_path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "metrics", "30-7-Test-Result", "azure_metric", os.path.basename(file))
            save_data(azure_data, output_path)


if __name__ == "__main__":
    main()