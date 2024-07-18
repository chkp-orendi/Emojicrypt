
import string
import re
import os
import logging


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



# extract_answer if in the prompt it was requested for format $Answer: answer
def extract_answer(LLM_answer):
    ANSWER_PATTERN = r"(?i)Answer\s*:\s*([^\n]+)"
    match = re.search(ANSWER_PATTERN, LLM_answer)
    if match:
        return match.group(1)
    return None

# List is in the foramt for: [word1,words2,...]
def extract_list(LLM_answer):
    ANSWER_PATTERN = r'\[([^\]]+)\]'
    answer_list = re.findall(ANSWER_PATTERN,LLM_answer)
    if len(answer_list)>=1:
         answer_list=answer_list[-1] #return last occurrence of pattern.
    else:
        return []
    #print(answer_list)
    words_to_encrypt_list =[]
    for item in answer_list.split(","):
        words_to_encrypt_list.append(item)
    return []

# dict is in the foramt for: {word1:key1,words2:key2,...}
def extract_dict(LLM_answer):
    ANSWER_PATTERN = r'\[([^\]]+)\]'
    answer_list = re.findall(ANSWER_PATTERN,LLM_answer)
    if len(answer_list)>=1:
         answer_list=answer_list[-1] #return last occurrence of pattern.
    else:
        return []
    #print(answer_list)
    words_to_encrypt_list =[]
    for item in answer_list.split(","):
        words_to_encrypt_list.append(item)
    return []

def init_logs(log_path,test_case):
    # Expand the tilde to the full home directory path
    log_file_path = os.path.expanduser(log_path)

    # Ensure the directory exists
    #os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    logger = logging.getLogger(test_case)
    return logger



