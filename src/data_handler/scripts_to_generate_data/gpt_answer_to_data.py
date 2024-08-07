import json
import os
import re
import sys
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.utils.azure_client import get_answer

# This function would check every 'assistant' message and search for pattern. i.e "$SCENARIO: what is 1+1?"
# Then would make dict containing:
# {
#     'original_question': "what is 1+1?",
#     'original_answer':  "2"
# }

def extract_pattern_from_gpt_chat(message, pattern):
        match = re.search(pattern, message['content'])
        if match:
            return match.group(-1)
        return None


def convert_gpt_chat_to_data(data, pattern):
    new_generated_data = []
    for message in data:
        if message['role'] == "assistant":
            if (query := extract_pattern_from_gpt_chat(message, pattern)):
                print(query)
                answer = get_answer(query + "be concise")
                print(answer)
                new_generated_data.append({
                        'original_question': query,
                        'original_answer': answer
                })
    return new_generated_data

def generate_new_answers(data):
    new_generated_data = []
    for message in data:
        query = message['scenario']
        query = query.strip("\n \"") + " BE CONCISE"
        print(query)
        answer = get_answer(query,model="gpt-4o-2024-05-13", temp = 0.0, max_tokens= 500)
        print(answer)
        new_generated_data.append({
                'original_question': query,
                'original_answer': answer
        })
        print("_______________________________________________________________________________________")
    return new_generated_data

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    print("saved to: " + str(file_path))

def main():
    input_file_path = os.path.join(os.getenv("PROJECT_PATH"), "data", "29-07-good-take.json")
    json_data = load_data(input_file_path)

    pattern = r"\$SCENARIO\s*:\s*([^\n]+)"
    new_generated_data = generate_new_answers(json_data)
    save_data(new_generated_data, os.path.join(os.getenv("PROJECT_PATH"), "data", "new_gpt_generated_data.json"))

if __name__ == "__main__":
    main()