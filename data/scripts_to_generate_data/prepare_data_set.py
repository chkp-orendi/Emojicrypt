import ollama
import string
import re
import os
import pandas as pd
import json

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", 'libraries'))

import AzureApi


def update_chat_history(chat_history, role, content):
        chat_history.append({
        'role': role,
        'content': content,
    })
        
def delete_last_entry_chat_history(chat_history, n):
    chat_history =chat_history[:-n]


def load_chat_history(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def talk_to_llm(model, temperature):
    chat_history = []
    messages_for_loop = []
    print("starting\n")
    for i in range(50):
        user_input = input()
        if (user_input == "MAGIC!"):
            break
        update_chat_history(chat_history, "user", user_input)
        messages_for_loop.append(user_input)
        azure_answer = AzureApi.get_answer_with_histroy(chat_history, model, temperature)
        print(azure_answer)
        update_chat_history(chat_history, "assistant", azure_answer)
    
    print("data set size:")
    try:
        data_size = int(input())
    except:
        return "FAILED, INVALID number of loops"
    print("number of user messages to loop over:")
    try:
        loop_size = int(input())
    except:
        return "FAILED, INVALID number of loops"
    user_inputs = messages_for_loop[-loop_size:]

    data = []
    for i in range(data_size):
        print(i)
        delete_last_entry_chat_history(chat_history, loop_size)
        for user_input in user_inputs:
            update_chat_history(chat_history, "user", user_input)
            azure_answer = AzureApi.get_answer_with_histroy(chat_history, model, temperature)
            update_chat_history(chat_history, "assistant", azure_answer)
            data.append(azure_answer)

    return data

def label_data(data):
    labeled_data = []
    for element in data:
        if "$SCENARIO" in element:
            scenario = element ##need to extract from it
        if "$LIST" in element:
            list_of_words = element ## need to extract from it
            labeled_data.append({"scenario": scenario, "list": list_of_words})
    return labeled_data
if __name__ == "__main__":
    data = talk_to_llm("gpt-4o-2024-05-13", 0.7)
    print(data)
    labeled_data = label_data(data)
    output_full_path = os.path.join(os.path.dirname(__file__), "testing_data.json")
    with open(output_full_path, 'w') as file:
        json.dump(labeled_data, file, indent=4)