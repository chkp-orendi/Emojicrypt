import os
import json

## This changes prompt_metric and answer_metric from single value to dict of values (of len 1)


data_path = "C:\\Users\\orendi\\Documents\\EmojiCrypt-main\\Emojicrypt\\testers\\metrics\\30-7-Test-Result\\embedding_metric"

inputfile_path = os.path.join(data_path, "2024-07-30-metrics-WrongAndFake.json")
with open(inputfile_path, 'r') as file:
    data = json.load(file)

copy_data = []
for obfuscator in data:
    obfuscator_data = []
    for prompt_dict in obfuscator[1]:
        answer_value = prompt_dict["answer_metric"]["answer_value"]
        prompt_dict["answer_metric"] =  answer_value
        prompt_similarity =  prompt_dict["prompt_metric"]["similarity"]
        prompt_leftovers =  prompt_dict["prompt_metric"]["leftovers"]
        prompt_dict["prompt_similarity"] =  prompt_similarity
        prompt_dict["prompt_leftovers"] =  prompt_leftovers
        prompt_dict.pop("prompt_metric")
        
        obfuscator_data.append(prompt_dict)
    copy_data.append([obfuscator[0], obfuscator_data])

with open(inputfile_path, 'w') as file:
    json.dump(copy_data, file, indent=4)