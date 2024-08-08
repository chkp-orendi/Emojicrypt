import sys
import os
import json
from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

with open(os.path.join(os.getenv("PROJECT_PATH"),"data","29-07-good-take.json"), 'r') as file:
    data_with_list = json.load(file)
with open(os.path.join(os.getenv("PROJECT_PATH"),"data","new_gpt_generated_data.json"), 'r') as file:
    data = json.load(file)

for i in range(len(data)):
    data[i]["list"] = data_with_list[i]["list"]

json.dump(data, open(os.path.join(os.getenv("PROJECT_PATH"),"data","08-08_gpt_4o_QNA_with_list.json"), 'w'), indent=4)