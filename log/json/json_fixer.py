import json
import math
import re

def extract_list(LLM_answer):
    LLM_answer = LLM_answer.replace('"', '')
    ANSWER_PATTERN = r'\$LIST:\s*\[([^\]]+)\]'
    answer_list = re.findall(ANSWER_PATTERN,LLM_answer)
    if len(answer_list)>=1:
         answer_list=answer_list[-1] #return last occurrence of pattern.
    else:
        return []
    #print(answer_list)
    words_to_encrypt_list =[]
    for item in answer_list.split(","):
        words_to_encrypt_list.append(item)
    return words_to_encrypt_list

def extract_scenarios_and_lists(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    

    scenarios_and_lists = []
    
    for i in range(math.floor(len(data['data'])/4) - 1):
        scenario = data['data'][4*i+1]['content']
        print(data['data'][4*i+3]['content'])
        words_list = extract_list(data['data'][4*i+3]['content'])
        scenarios_and_lists.append({
                    'scenario': scenario,
                    'list': words_list
                })
    return scenarios_and_lists



text = """
Sure, here's a list of words from the scenario that could be considered technical terms or sensitive information:
$LIST: ["Gamma Gardening", "landscaping company", "Delta Developments", "property development company", "landscape a new residential complex", "contract", "complete the landscaping", "three months", "maintain the gardens", "one year", "not completed", "not up to the agreed standard", "legal action", "breach of contract", "contractual obligations", "severe weather conditions", "supply chain disruptions"]
"""
print(extract_list(text))

# def save_extracted_data(extracted_data, output_filename):
#     with open(output_filename, 'w') as file:
#         json.dump(extracted_data, file, indent=4)

# # Example usage
# input_filename = 'generated_data_temp0.json'
# output_filename = 'extracted_data_temp0.json'

# extracted_data = extract_scenarios_and_lists(input_filename)
# save_extracted_data(extracted_data, output_filename)
# input_filename = 'more_generated_data_temp0.json'
# output_filename = 'more_extracted_data_temp0.json'

# extracted_data = extract_scenarios_and_lists(input_filename)
# save_extracted_data(extracted_data, output_filename)

# print(f"Extracted data has been saved to {output_filename}.")
