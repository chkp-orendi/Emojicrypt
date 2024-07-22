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

def update_chat_history(chat_history, role, content):
    chat_history.append({
    'role': role,
    'content': content,
})
def delete_entry_chat_history(chat_history, i):
    chat_history.pop(i)

# chat_history =[]
#     update_chat_history(chat_history, "user", "Are you famliar with real world examples where people included private buisness information in their llm questions?")
#     azure_answer = AzureApi.get_answer_with_histroy(chat_history, "gpt-4", 0.0)
#     print(azure_answer)
#     update_chat_history(chat_history,"assistant",azure_answer)
#     update_chat_history(chat_history, "user", "Can you generate the actual based on the hypothetical cases you have listed?")
#     azure_answer = AzureApi.get_answer_with_histroy(chat_history, "gpt-4", 0.0)
#     print(azure_answer)
#     update_chat_history(chat_history,"assistant",azure_answer)
#     update_chat_history(chat_history, "user", """Can you focus on Product Development?
# and give me a list of terms containing SENSETIVE DATA that appear in the prompt""")
#     azure_answer = AzureApi.get_answer_with_histroy(chat_history, "gpt-4", 0.0)
#     print(azure_answer)
#     update_chat_history(chat_history,"assistant",azure_answer)

def load_chat_history(filename):
    with open(filename, 'r') as file:
        return json.load(file)['data']

def talk_to_llm(model, temperature):
    chat_history = []
    for i in range(50):
        user_input = input()
        if (user_input == "SUPER MAGIC!"):
            break
        update_chat_history(chat_history, "user", user_input)
        azure_answer = AzureApi.get_answer_with_histroy(chat_history, model, temperature)
        print(azure_answer)
        update_chat_history(chat_history, "assistant", azure_answer)
    
    data = []
def process_file():
    data = []
    chat_history =load_chat_history('/root/Emoji/Emojicrypt/log/json/generated_data2.json')

    for i in range(50):
        print(i)
        delete_entry_chat_history(chat_history, -1)
        delete_entry_chat_history(chat_history, -1)
        delete_entry_chat_history(chat_history, -1)
        delete_entry_chat_history(chat_history, -1)
        user_input = "Can you give me another scenario with mock data and fake names?"
        #update_chat_history(data, "user", user_input)
        update_chat_history(chat_history, "user", user_input)
        azure_answer = AzureApi.get_answer_with_histroy(chat_history, "gpt-4", 0.3)
        update_chat_history(chat_history, "assistant", azure_answer)
        update_chat_history(data, "assistant", azure_answer)
        print(azure_answer)
        user_input = "Can you provide a list of words that are technical terms or sensetive information in the format $LIST: [word1, word2,...]"
        update_chat_history(chat_history, "user", user_input)
        azure_answer = AzureApi.get_answer_with_histroy(chat_history, "gpt-4", 0.3)
        update_chat_history(chat_history, "assistant", azure_answer)
        update_chat_history(data, "assistant", azure_answer)
        print(azure_answer)

    # Save the data to a JSON file
    with open('/root/Emoji/Emojicrypt/log/json/generated_data_temp0.3.json', 'w') as outfile:
        json.dump({"data": data}, outfile, indent=4)

if __name__ == "__main__":
    talk_to_llm("gpt-4", 0.3)
    #process_file()
