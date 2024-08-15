import json
import os
import sys
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


    def load_chat_history(self,file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            for message in data:
                self.update_chat_history(message['role'], message['content'])
        self.messages_for_loop = [self.chat_history[-2]]

    def start_chat(self):
        print("starting chat")
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
                    self.messages_for_loop.append(user_input)
                    azure_answer = get_answer_with_histroy(self.chat_history, self.model, self.temperature)
                    print(azure_answer)
                    self.update_chat_history("assistant", azure_answer)
        self.messages_for_loop = [self.messages_for_loop[i] for i in range(1, len(self.messages_for_loop), 2)]

        #save history for loading later
        file_path = os.path.join(os.getenv("PROJECT_PATH"),"src","data_handler", "scripts_to_generate_data" ,"chat_history_yoni.json")
        with open(file_path, 'w') as file:
                json.dump(self.chat_history, file, indent=4)

        print("loop size:\n")
        return input()

    def generate_data(self, data_size, loop_size):
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

    def save_data(self, file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)


def main():
    model = "gpt-4o-2024-05-13"
    temperature = 0.0
    chat_generate_query = chat_gpt(model, temperature)
    file_path = os.path.join(os.getenv("PROJECT_PATH"),"src","data_handler", "scripts_to_generate_data" ,"chat_history_yoni.json")

    # chat_generate_query.load_chat_history(file_path)
    loop_size = chat_generate_query.start_chat()
    chat_generate_query.generate_data(3, int(1))

    
    output_file_path = os.path.join(os.getenv("PROJECT_PATH"),"data","15-08-2024" ,"new_generated_data.json")
    chat_generate_query.save_data(output_file_path, chat_generate_query.generated_data)
    print("Data saved at: ", output_file_path)

if __name__ == "__main__":
    main()






