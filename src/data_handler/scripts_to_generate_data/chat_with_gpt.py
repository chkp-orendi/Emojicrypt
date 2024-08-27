import json
import os
import sys
from datetime import datetime
from typing import List, Dict
import random

from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.utils.azure_client import get_answer_with_histroy


class chat_gpt:


    def __init__(self, model, temperature):
        self.model = model
        self.temperature = temperature

        self.chat_history = []
        self.messages_for_loop = []
        self.generated_data = []

    def update_chat_history(self, role, content):
            self.chat_history.append({
            'role': role,
            'content': content,
        })
            
    def delete_last_entry_chat_history(self, n):
        self.chat_history =self.chat_history[:-n]



    def load_chat_history_from_file(self, file_path: str, loop_size: int):
        """
        load to chat_history from file_path.
        loop_size is the number of last user messages to loop over.
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
            for message in data:
                self.update_chat_history(message['role'], message['content'])

    def load_chat_history_from_list(self,new_chat_history: List[Dict]):
        """
        load to chat_history from List.
        """
        self.chat_history = new_chat_history

    def load_messages_for_loop(self, messages_for_loop: List[str]):
        self.messages_for_loop = messages_for_loop

    def start_chat(self):
        print("starting chat")
        messages_for_loop = []
        while True:
            user_input = input()
            match user_input:
                case "BREAK!":
                    break
                case "REVERT!":
                    self.delete_last_entry_chat_history(2)
                    continue
                case _:
                    self.update_chat_history("user", user_input)
                    messages_for_loop.append(user_input)
                    azure_answer = get_answer_with_histroy(self.chat_history, self.model, self.temperature)
                    print(azure_answer)
                    self.update_chat_history("assistant", azure_answer)
        self.messages_for_loop = [messages_for_loop[i] for i in range(1, len(messages_for_loop), 2)]

        #save history for loading later
        file_path = os.path.join(os.getenv("PROJECT_PATH"),"src","data_handler", "scripts_to_generate_data" ,"chat_history_yoni.json")
        with open(file_path, 'w') as file:
                json.dump(self.chat_history, file, indent=4)

        print("loop size:\n")
        return input()

    def generate_data(self, data_size, loop_size):
        if loop_size == "0":
            self.generated_data = self.chat_history ##save history
            return
        data = []
        for i in range(data_size):
            print(i)
            self.delete_last_entry_chat_history(2*loop_size) #need to delete user messages and assistant messages
            for user_input in self.messages_for_loop[-loop_size:]:
                # user_input = user_input["content"]
                self.update_chat_history("user", user_input)
                azure_answer = get_answer_with_histroy(self.chat_history, self.model, temp =1.2)
                print(azure_answer)
                print("_____________________________")
                self.update_chat_history("assistant", azure_answer)
                
                data.append({"user" : user_input, "assistant" : azure_answer})
        self.generated_data = data
        
    def set_random_history_pool(self, path: str):
        with open(path, 'r') as file:
            prompts_examples = json.load(file)
    
        user_and_assistant_prompts_list = [] # will have list of pairs of user and assistant prompts
        for index in range (int(len(prompts_examples)/2)):
            user_and_assistant_prompts_list.append([prompts_examples[2*index],prompts_examples[2*index+1]])
            
        self.random_history_pool = user_and_assistant_prompts_list

    def get_random_history(self):
        random_sublist = random.sample(self.random_history_pool, 4)
        random_sublist = [item for sublist in random_sublist for item in sublist] # return list to original format
        self.load_chat_history_from_list(random_sublist)

    def generate_answer(self):
        for user_input in self.messages_for_loop:
            self.update_chat_history("user", user_input)
            azure_answer = get_answer_with_histroy(self.chat_history, self.model, temp =1.2)
            self.update_chat_history("assistant", azure_answer)
        return self.chat_history[-2*len(self.messages_for_loop)+1::2]
    
    def save_data(self, file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)


def main():
    model = "gpt-4o-2024-05-13"
    temperature = 0.0
    chat_generate_query = chat_gpt(model, temperature)
    file_path = os.path.join(os.getenv("PROJECT_PATH"),"data","20-08-2024", "Context_Answer_different_topics_examples.json")
    
    chat_generate_query.set_random_history_pool(file_path)
    chat_generate_query.load_messages_for_loop(["give me another example"])

    data = []
    for i in range(100):
        print(i)
        chat_generate_query.get_random_history()
        data.append(chat_generate_query.generate_answer())
    
    # loop_size = 1
    # loop_size = chat_generate_query.start_chat()
    # chat_generate_query.generate_data(20, loop_size)

    
    output_file_path = os.path.join(os.getenv("PROJECT_PATH"),"data","20-08-2024" ,"Context_Answer_different_topics" + datetime.now().strftime("_%H_%M") +".json")
    chat_generate_query.save_data(output_file_path, data)
    print("Data saved at: ", output_file_path)

if __name__ == "__main__":
    main()






