import ollama
import string
import re
import os
import logging

def emoji_encrypt_text(text, client ,model='llama3:8b'):
    # try a prompt claiming after : its user and not privlage
    encypt_pompt = "in the following text try to change sensetive data with symbols, emojis, special chareters. return ONLY the converted text and NOTHING more. text: "
    answer = client.generate(model = model, prompt = encypt_pompt + text)
#    return answer["response"]
    return text
#normalize and check_match are used in drop_eval, might be useful for other testers

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


def extract_answer(LLM_answer):
    match = re.search(ANSWER_PATTERN, LLM_answer)
    if match:
        return match.group(1)
    return None


def init_logs(log_path,test_case):
    # Expand the tilde to the full home directory path
    log_file_path = os.path.expanduser(log_path)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logger = logging.getLogger(test_case)
    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    if test_case == 'w':
        logger.info('Started winogrande_eval.py')
    elif test_case == 'd':
        logger.info('Started drop_eval.py')
    elif test_case == 'h':
        logger.info('Started hellaswag_eval.py')
    elif test_case == 'e':
        logger.info('Started embedding_eval.py')
    elif test_case == 'm':
        logger.info('Starting init')

    return logger
