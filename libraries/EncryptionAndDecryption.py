import ollama
import string
import re
import os
import logging



log_path = '~/Emoji/Emojicrypt/log/wrong_format_encryption.log'

def get_prompt_to_get_list(text):
    return f"""the following text contains a context (following 'context:') and a question about the context (following 'question'):
    {text}
    can you identify all of the words in the context that can be defined as: technical terms, acronyms, corporate lingo. please list these words in the following format: [word1, word2, ..., wordN]. in addition, can you specify which of the words in the list are required to effectively answer the question?"""

def get_prompt_to_get_list2(text):
    return f"""In the following text:
    "{text}"
    Create a list of technical terms, acronyms that are not directly addressed in the question. Explain your tought process and at the end write a line of the foramt $LIST: [word1, word2, word3, ...]
    """
def get_prompt_to_get_dict(text, words_to_encrypt_list):
    return f"""
In the following text:
"{text}"
and list:  "{words_to_encrypt_list}"
Create emoji sequences for the words in the list. The emoji sequences should allow an LLM to correctly process the prompt but should not be easily interpreted by humans.
Explain your reason and at the end print format: $SEQUENCE:{{word1:sequences ,word2:sequences ,...}}
"""


def init_Ollama_client():
    client = ollama.Client(host='http://172.23.81.3:11434')
    return client

def get_encryption_dict(text, client ,model='llama3:8b'):
    # enc_logger = logging.getLogger('wrong format encryption')
    print("get_prompt_to_get_list(text): " + get_prompt_to_get_list(text))
    answer = client.generate(model = model, prompt = get_prompt_to_get_list(text))
    print("question I:" + answer["response"])

    answer_list = re.findall(r'\$LIST: \[([^\]]+)\]',answer["response"])
    if len(answer_list)>=1:
         answer_list=answer_list[-1] #return last occurrence of pattern.
    else:
        return {}
   
    print(answer_list)
    words_to_encrypt_list =[]
    for item in answer_list.split(","):
        words_to_encrypt_list.append(item)
    print("words_to_encrypt_list:")
    print(words_to_encrypt_list)
    print("__________________________")
    
    answer = client.generate(model = model, prompt = get_prompt_to_get_dict(text,words_to_encrypt_list))
    print("question II:" + answer["response"])

    encrypted_list = re.findall(r'\$SEQUENCE:\s*\{([^}]*)\}',answer["response"])
    if len(encrypted_list)>=1:
         encrypted_list=encrypted_list[-1] #return last occurrence of pattern.
    else:
        return {}

    encryption_dict ={}
    i = 0
    for item in encrypted_list.split(","):
        try:
            encryption_dict[item.split(":")[0].strip("'").strip('"')]=item.split(":")[1].strip("'").strip('"')
        except:
            print(f"error in {item}")
        i += 1
    print("encryption_dict III:")
    print(encryption_dict)

    return encryption_dict

def get_encryption_text(text, encryption_dict):
    words_in_text = text.split()  # Split the text into words
    total_words = len(words_in_text)  # Count the total number of words
    encrypted_text = text
    words_replaced = 0  # Initialize the counter to zero

    for key in encryption_dict.keys():
        if len(encryption_dict[key])<1 or len(key)<1:
            continue
        if key in encrypted_text:
            count = text.count(key)  # Count occurrences of the key in the text
            encrypted_text = encrypted_text.replace(key, encryption_dict[key])
            words_replaced += count  # Increment the counter by the number of replacements made
    
    if total_words > 0:  # To avoid division by zero
        percentage_words_replaced = (words_replaced / total_words)*100
    else:
        percentage_words_replaced = 0  # If the text is empty, set percentage to zero

    return encrypted_text, percentage_words_replaced


def get_decryption_text(encrypted_text, encryption_dict):
    decrypted_text = encrypted_text
    for key in encryption_dict.keys():
        if len(encryption_dict[key])<1 or len(key)<1:
            continue
        decrypted_text = decrypted_text.replace(encryption_dict[key],key)
    return decrypted_text
