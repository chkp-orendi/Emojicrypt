import ollama
import string
import re
import os
import logging

log_path = '~/Emoji/Emojicrypt/log/wrong_format_encryption.log'


## try prompt where we ask for a list with details
#{ 
#key:value - explaination
#}

def get_encryption_dict(text, client ,model='llama3:8b'):
    # enc_logger = logging.getLogger('wrong format encryption')
    prompt_to_get_list = f"""In the following text:
    "{text}"
    Create a list of technical terms and acronyms that are not directly addressed in the question. Explain your tought process and at the end write a line of the foramt $LIST: [word1, word2, word3, ...]
    """
    answer = client.generate(model = model, prompt = prompt_to_get_list)
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
    promt_to_get_encryption = f"""
In the following text:
"{text}"
and list:  "{words_to_encrypt_list}"
Create emoji sequences for the words in the list. The emoji sequences should allow an LLM to correctly process the prompt but should not be easily interpreted by humans.
Explain your reason and at the end print format: $SEQUENCE:{{word1:sequences ,word2:sequences ,...}}
"""
    answer = client.generate(model = model, prompt = promt_to_get_encryption)
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

def encrypt_text(text, encryption_dict):
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


def decrypt_text(encrypted_text, encryption_dict):
    decrypted_text = encrypted_text
    for key in encryption_dict.keys():
        if len(encryption_dict[key])<1 or len(key)<1:
            continue
        decrypted_text = decrypted_text.replace(encryption_dict[key],key)
    return decrypted_text

def normalize(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    s = s.lower()
    exclude = set(string.punctuation)
    s = "".join(char for char in s if char not in exclude)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = " ".join(s.split())
    return s

#s1 should be llm answer
def check_match(s1,s2, endings=None) -> bool:
    s1 = normalize(s1)
    s2 = normalize(s2)

    if s1 == "" or s2 == "":
        return s1 == s2
    # I added this if the LLM does not respond with number. Need to update tests to see if it works.
    elif not s1.isnumeric() and endings!=None:
        return s1 in endings[s2] or endings[s2] in s1
    
    return s1 in s2 or s2 in s1

ANSWER_PATTERN = r"(?i)Answer\s*:\s*([^\n]+)"

# extract_answer if in the prompt it was requested for format $Answer: answer
def extract_answer(LLM_answer):
    match = re.search(ANSWER_PATTERN, LLM_answer)
    if match:
        return match.group(1)
    return None


def init_logs(log_path,test_case):
    # Expand the tilde to the full home directory path
    log_file_path = os.path.expanduser(log_path)

    # Ensure the directory exists
    #os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    logger = logging.getLogger(test_case)
    return logger



