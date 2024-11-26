import sys
import re
from typing import Dict
import re
import sys
import os
import json
import datetime


from src.utils.azure_client import AzureClient
from src.Obfuscators.phase_1_obfuscator import PhaseOneObfuscator
"""
This is a prototype obfuscator I will pass to the GW to see how it works.
"""

azure_llm_wrapper_factory = lambda :AzureClient("azure_client",  "../", "gpt-4o-2024-05-13", 0.0)
prefix = """
Do not explain the emojis in your answer and other than the exact emoji sequences from the original prompt, do not use emojis in your answer.\n
"""
obfuscator = PhaseOneObfuscator(name = "prototype", llm_wrapper_factory=azure_llm_wrapper_factory, prompt_prefix=prefix, lower_bound_percentage = 75, upper_bound_percentage = 95)


def process_input(input_string, original_prompt):
    """
    return response_answer, deobfuscated_response_answer,response_body
    """
    fixed_client_prompt = 0
    json_contain_p = 0

    lines = input_string.split("\n")
    result = ""
    
    response = ""
    for i in range(0, len(lines)):
        changed = False
        # print(lines[i])
        # Extract event and JSON part
        if (lines[i][:7] != "data: {"):
            result += lines[i] + "\n"
            continue
        data_str = lines[i].strip()[5:]  # Skip 'data: '
        
        # Convert string to JSON (dict)
        data_json = json.loads(data_str)
        print(data_json)
        if fixed_client_prompt <= 2 and 'v' in data_json:
            if 'message' in data_json['v']:
                if isinstance(data_json['v'], dict) and 'message' in data_json['v']:
                    if fixed_client_prompt ==1:
                        data_json['v']['message']['content']['parts'][0] = original_prompt
                        fixed_client_prompt += 1
                        changed = True
                    else:
                        fixed_client_prompt += 1
                        changed = True

        # last append
        # print(data_json)
        if 'v' in data_json:
            if isinstance(data_json['v'], list):
                response_answer = response + data_json['v'][0]['v']
                deobfuscated_response_answer = obfuscator.deobfuscate(response_answer)
                data_json['v'][0]['v'] = deobfuscated_response_answer
                changed = True
        else:
            response += str(data_json)
            changed = True
        if not changed:
            response += str(data_json['v']) 
            data_json['v'] = ""
        

        # Convert the modified JSON object back to string
        modified_data_str = json.dumps(data_json)
        result += "data: " + modified_data_str + "\n"
        # Append the result in the desired format
    
    # Join everything back into a single string
    return response_answer, deobfuscated_response_answer, result


def main():
    start_time = datetime.datetime.now()
    with open('/home/admin/Emojicrypt/input.txt', 'r') as file:
        response_body = file.read()
    
    with open('/home/admin/Emojicrypt/encryption_dictonary.json', 'r', encoding='utf-8') as file:
        encryption_dictonary = json.loads(file.read())


    with open('/home/admin/Emojicrypt/original_prompt.txt', 'r', encoding='utf-8') as file:
        original_prompt = file.read()
        original_prompt = original_prompt.encode('utf-8').decode('unicode_escape')

    obfuscator._dictionary_used = encryption_dictonary
    # obfuscator.set_encryption(encryption_dictonary)

    if obfuscator.get_dictionary(): #did not obfuscate
        response_answer, deobfuscated_response_answer, deobfuscated_response_body = process_input(response_body, original_prompt)
    else:                           #need to convert back
        response_answer = "no changes needed"
        deobfuscated_response_body = response_body

    with open('/home/admin/Emojicrypt/output.txt', 'w') as file:
        file.write("MAGIC" + deobfuscated_response_body)
        file.flush()

    end_time = datetime.datetime.now()
    time = end_time-start_time
    with open('/home/admin/Emojicrypt/info.txt', 'a', encoding = 'utf-8') as file:
        file.write("\n___________________________________________________________________________RESPONSE_______________________________________________________________________________________________________\n")
        file.write(response_answer + "\n")
        file.write("_________________________________________________________________________________________________________________________________________________________________________________________\n")
        file.write(deobfuscated_response_answer + "\n")
        file.write("_________________________________________________________________________________________________________________________________________________________________________________________\n")
        file.write(f"time: {time}\n")
        file.flush()

    
if __name__ == '__main__':
    print("starting\n")
    main()

