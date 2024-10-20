import os
import sys
import json
from dotenv import load_dotenv
import numpy as np
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))


from src.Evaluators.CompareOriginalAndGuessed import get_dictionary
from src.utils.string_utils import smart_replace
import markdown



def main():
    with open(os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024","2024-09-04", "Presentation","Original Movie Results_2.json"), 'r', encoding='utf-8') as file:
        data = json.load(file)

    output_path = os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024","2024-09-04", "decryption sample")


    text = ""
    for obfuscator in data:
        for index, case in enumerate(obfuscator[1]):
            if "ANSWER: 0.8\n\nThe similarity score is 0.8 because the majority of the technical terms in Text1 have been replaced with emojis in Text2" in case["prompt_metric reasoning"][0]:
                print(index)
                obfuscation_dict = get_dictionary(case["gusses for emojis"])
                text += f"<b>{obfuscator[0]} {index}</b><br>\n"
                text += f"<b>original prompt:</b> {case['original_prompt']}<br>\n"

                dycrpyted_obfuscated_answer = smart_replace(case["obfuscated_prompt"], obfuscation_dict)
                text += f"<b>dycrpyted obfuscated answer:</b> {dycrpyted_obfuscated_answer}<br>\n"
                text += f"<b>obfuscation_dict:</b> {obfuscation_dict}<br>\n"


    text = markdown.markdown(text)
    with open(os.path.join(output_path, f"result sample.html"), 'w', encoding='utf-8') as file:
        file.write(text)


if __name__== "__main__":
    main()
