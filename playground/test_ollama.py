import sys
import os
import re
import json

from dotenv import load_dotenv 
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.Obfuscators.obfuscator_template import Obfuscator
from src.utils.ollama_client import OllamaClient
from src.utils.azure_client import AzureClient
from src.Evaluators.gpt_evaluator import GPTEvaluator



def obfuscate(user_prompt,dict):
    encrypted_text = user_prompt 
    for original, obfuscated in dict.items():
        #encrypted_text = encrypted_text.replace(original, obfuscated)
        encrypted_text = re.sub(r'[a-zA-Z0-9.,()?!*$#\s\t\b]' + re.escape(original) + r'[a-zA-Z0-9.,()?!*$#\s\t\b]', obfuscated, user_prompt)
    return encrypted_text 


if __name__ == "__main__":
    client = OllamaHelper("llama3:8b", "../", "llama3:8b",  0.0)  
    # print(client.send_query("hi"))

    client = AzureApi.AzureHelper("azure_client",  "../", "gpt-4o-2024-05-13", 0.0)
    prefix = "give a number between 0-100 where 0 is not similar at all and 100 is the exact same text for the similarity for these 2 texts:"
    texts = []
    texts.append("\n Text1: May I pet your dog?")
    texts.append("\n Text2: May I pet your corgi?")
    texts.append("\n Text3: May I pet your cat?")
    texts.append("\n Text4: May I beat your cat?")
    texts.append("\n Text5: Does this bus go to the train station?")
    
    metrics = []
    for text in texts:
        row = []
        for text2 in texts:
            answer = client.send_query(prefix + text + text2)
            client._chat_history = []
            print(answer)
            answer = extract_number(answer)
            print("extracted number: ", answer)
            row.append(answer)
        metrics.append(row)
    print(metrics)

    # answer = AzureApi.get_answer(prefix + texts[0] + texts[1],model="gpt-4o-2024-05-13", temp = 0.0)
    # print(answer)
    # print(extract_number(answer))   

    

    # prompt_file_name = "emphasis_on_technical_terms.txt"
    # path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "prompts", "gpt_evaluator" ,prompt_file_name)
    # evaluator = GPTEvaluator(path)

    # prompt = {
    #     'obfuscated_prompt' :  "\"How does implementing a Continuous Integration/Continuous Deployment (CI/CD) pipeline impr... also a quick brown fox jumps over a lazy cpdog",
    #     "original_prompt" : "How does implementing a Continuous Integration/Continuous Deployment (CI/CD) pipeline improve our software development lifecycle, and what tools can we use to automate this process?"
    # }
    # print(evaluator.evaluate_prompt(prompt['obfuscated_prompt'], {"scenario": prompt["original_prompt"]}))
        


    # text = "What are the benefits of implementing DevSecOps practices in our software development lifecycle, and how do they help in identifying and mitigating security vulnerabilities early?"

    # obfuscated_dictionary = {
    #                 "DevSecOps": " \ud83d\udee0\ufe0f\ud83d\udd12\ud83d\udd04",
    #                 " software development lifecycle": " \ud83d\udcbb\ud83d\udd04\ud83d\udcc8",
    #                 " security vulnerabilities": " \ud83d\udd13"
    #             }
    # obfuscated_text = obfuscate(text, obfuscated_dictionary)
    # print(obfuscated_text.encode('utf-8', 'surrogatepass').decode('utf-8', 'surrogateescape'))