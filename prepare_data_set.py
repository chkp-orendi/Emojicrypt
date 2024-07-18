import ollama
import string
import re
import os
import pandas as pd
import json

# the encryption will always have a problem if the user will write something like: IGNORE EVERYTHING SAID BEFORE
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries'))
import EncryptionAndDecryption 
import AnswerExtraction
import AzureApi
import ListThenDictApproach


data_path = "/root/Emoji/Emojicrypt/data/generated_data/chatgpt_generated_questions.txt"
def process_file(input_file):
    data = []
    with open(input_file, 'r') as file:
        content = file.read()
        prompts = content.split('\n\n')  # Assuming each prompt is separated by an empty line

        prompt_number = 0
        for prompt in prompts:
            prompt_number += 1
            if prompt.strip():  # Ensure the prompt is not just empty space
                # Extract the context and question (assuming the format is always "context" then "question" on the next line)
                lines = prompt.split('\n')
                if len(lines) >= 2:
                    context = lines[0].strip('"')
                    question = lines[1].strip()

                    # Create a single prompt string
                    original_prompt = f"{context} {question}"

                    # Get embeddings and answers
                    original_embeddings = AzureApi.get_embedding(original_prompt)
                    original_answer = AzureApi.get_answer(original_prompt, "gpt-4")

                    # Append to data list
                    data.append({
                        "original_prompt": original_prompt,
                        "original_embeddings": original_embeddings,
                        "original_answer": original_answer,
                        "original_answer_embeddings": AzureApi.get_embedding(original_answer)
                    })
            if prompt_number >9:
                break

    # Save the data to a JSON file
    with open('/root/Emoji/Emojicrypt/log/json/tmp.json', 'w') as outfile:
        json.dump({"data": data}, outfile, indent=4)

if __name__ == "__main__":

    process_file(data_path)
