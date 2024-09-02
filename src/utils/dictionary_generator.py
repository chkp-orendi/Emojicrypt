import os
from dotenv import load_dotenv 
import sys
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

import json
from src.Obfuscators.obfuscator_template import Obfuscator



class DictionaryGenerator:
    def __init__(self, obfuscator_class: Obfuscator):
        self.obfuscator = obfuscator_class

    def generate(self, data: list) -> dict:
        """
        This function will generate a dictionary from the data given to it
        """
        new_data = {}

        for index, line in enumerate(data):
            print(index)
            self.obfuscator.obfuscate({"original_prompt": line})
            line_dictionary = self.obfuscator.get_dictionary()
            print(line_dictionary)
            new_data.update(line_dictionary)
        
        return new_data





from src.Obfuscators.context_reletive_obfuscator import ContextReletiveObfuscator
from src.utils.azure_client import AzureClient
from src.utils.ollama_client import OllamaClient

azure_llm_wrapper_factory = lambda :AzureClient("azure_client",  "../", "gpt-4o-2024-05-13", 1.0)

prompt_list = """
Convert the following text to a list of technical terms in the format $LIST: [ex1, ex2, ...]
Make sure the terms are in the text exactly and try to list many words.
Here are examples how to use all the rules to make a list to the text with the format $LIST: [ex1, ex2, ...].

Example:
Alligators are powerful reptiles commonly found in freshwater habitats such as swamps, rivers, and lakes in the southeastern United States. These ancient creatures have been around for millions of years, surviving through various environmental changes. Alligators are apex predators, meaning they sit at the top of the food chain, feeding on a variety of animals, including fish, birds, and small mammals. Despite their fearsome reputation, alligators are generally shy and avoid human contact unless provoked or threatened.
What is the role of alligators in their ecosystem, and how do they typically interact with humans?

Out put: $LIST: [Alligators ,powerful reptiles, freshwater, swamps, rivers, Lakes, Apex predators, Food chain, Environmental changes, Ecosystem, feeding, animals, fish, birds, mammals, fearsome, human contact, provoked, threatened]


Now convert the following text:
{text}
"""
prompt_dict = """
Given the following list {lst}
Provided an obfuscator for the words in relation to the context using complex emojis sequence that will be hard to understand by a human but will be understood by llm. The keys and values shuld be UNIQUE.
Return in the format $Dict [value1:obfuscator1, value2: obfuscator2,....]

Example:
List: [Alligators ,powerful reptiles, freshwater, swamps, rivers, Lakes, Apex predators, Food chain, Environmental changes, Ecosystem]
Output: $Dict: [Alligators: 🐊🌿🌊🦷 ,powerful reptiles: 💪🦎🛡️🔥, freshwater: 💧🚰🏞️🌀🐟, swamps: 🌾🐸🪵, rivers: 🏞️⛵🐠🌊, Lakes: 🌊🐢, Apex predators: 🔝🦁💥, Food chain: 🍽️🔗🍗, Environmental changes: 🌍🔄🌀, Ecosystem: 🏞️🔄🦋, feeding:🍴🍖🍲 , animals: 🦓🦔🐾, fish:🎣🐟 , birds: 🦅🕊️, mammals:🦣🦇🧬, fearsome :🧛‍♂️👹😱, human contact: 👤👀🚫, provoked:🚨🆘⚠️, threatend: ⚔️🛡️]

Now return $Dict on the list you provided
"""


obfuscator = ContextReletiveObfuscator("Context_Reletive_Obf",azure_llm_wrapper_factory, prompt_list=[prompt_list, prompt_dict])

generator = DictionaryGenerator(obfuscator)

data_path = os.path.join(os.getenv("PROJECT_PATH"),"data","29-08-2024","movie_P&Q_data_for_dict.json")

with open(data_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
# print(data[0])
new_dict = generator.generate(data)

output_path = os.path.join(os.getenv("PROJECT_PATH"),"data","29-08-2024","generated_dict.json") 

with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(new_dict, file, ensure_ascii=False, indent=4)   