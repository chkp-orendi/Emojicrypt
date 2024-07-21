import json
import math


def extract_list(LLM_answer):
    ANSWER_PATTERN = r'$LIST:\s*\[([^\]]+)\]'
    answer_list = re.findall(ANSWER_PATTERN,LLM_answer)
    if len(answer_list)>=1:
         answer_list=answer_list[-1] #return last occurrence of pattern.
    else:
        return []
    #print(answer_list)
    words_to_encrypt_list =[]
    for item in answer_list.split(","):
        words_to_encrypt_list.append(item)
    return []


def extract_scenarios_and_lists(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    

    scenarios_and_lists = []
    
    for i in range(math.floor(len(data['data'])/4) - 1):
        scenario = data['data'][4*i+1]['content']
        words_list = data['data'][4*i+3]['content']
        scenarios_and_lists.append({
                    'scenario': scenario,
                    'list': words_list
                })
    return scenarios_and_lists

def save_extracted_data(extracted_data, output_filename):
    with open(output_filename, 'w') as file:
        json.dump(extracted_data, file, indent=4)

# Example usage
input_filename = 'generated_data3.json'
output_filename = 'extracted_data.json'

extracted_data = extract_scenarios_and_lists(input_filename)
save_extracted_data(extracted_data, output_filename)

print(f"Extracted data has been saved to {output_filename}.")
