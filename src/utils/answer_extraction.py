
import string
import re
import os
import logging
from typing import Optional

def normalize(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    s = s.lower()
    exclude = set(string.punctuation)
    s = "".join(char for char in s if char not in exclude)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = " ".join(s.split())
    return s


# extract_answer if in the prompt it was requested for format $Answer: answer
def extract_answer(LLM_answer: str) -> Optional[str]:
    ANSWER_PATTERN = r"(?i)Answer\s*:\s*([^\n]+)"
    match = re.search(ANSWER_PATTERN, LLM_answer)
    if match:
        return match.group(1)
    return None

# List is in the foramt for: $LIST: [word1,words2,...]
def extract_list(LLM_answer: str) -> list:
        ANSWER_PATTERN = r'\$LIST:\s*\[(.*?)\]'
        answer_list = re.findall(ANSWER_PATTERN, LLM_answer)
        if len(answer_list) >= 1:
            last_occurrence = answer_list[-1]  # return last occurrence of pattern.
        else:
            return []

        return [token.strip("' \t") for token in last_occurrence.split(',')]


# dict is in the foramt for: $Dict:  {word1:key1,words2:key2,...}
def extract_dict(LLM_answer):
        ANSWER_PATTERN = r'\$Dict:\s*\[(?:\s*[^:\[\],]+:[^:\[\],]+\s*,)*\s*[^:\[\],]+:[^:\[\],]+\s*\]'
        answer_list = re.findall(ANSWER_PATTERN, LLM_answer)
        if len(answer_list) >= 1:
            answer_list = answer_list[-1]  # return last occurrence of pattern.
        else:
            return {}
        words_replacements = {}
        answer_list = answer_list.replace("$Dict:", "").strip("[] \"")
        print(answer_list)
        for item in answer_list.split(","):
            splited_item = item.split(":")
            if len(splited_item) !=2:
                print("INVALID ITEM")
                print(item)
                print(LLM_answer)
                continue
            words_replacements[item.split(":")[0].strip("' \t")] = item.split(":")[1].strip("' \t")
        return words_replacements

def extract_number(text: str) -> float:
    # Use regular expression to find all numbers in the text
    pattern = r'\$ANSWER: (-?\d+\.\d+|-?\d+)'

    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    else:
        return None
    
    
def init_logs(log_path: str,test_case: str) -> logging.Logger:
    log_file_path = os.path.expanduser(log_path)

    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    logger = logging.getLogger(test_case)
    return logger

def smart_replace(text: str, replacements: dict[str,str]) -> str:
    replaced_text = text
    break_word_characters = [
    ' ',  # Space
    '\t',  # Tab
    '\n',  # Newline
    '\r',  # Carriage return
    '.',  # Period
    ',',  # Comma
    ';',  # Semicolon
    ':',  # Colon
    '!',  # Exclamation mark
    '?',  # Question mark
    '-',  # Hyphen
    '_',  # Underscore
    '(',  # Open parenthesis
    ')',  # Close parenthesis
    '[',  # Open bracket
    ']',  # Close bracket
    '{',  # Open brace
    '}',  # Close brace
    '"',  # Double quote
    "'",  # Single quote
    '/',  # Forward slash
    '\\',  # Backslash
    '|',  # Vertical bar
    '@',  # At symbol
    '#',  # Hash
    '$',  # Dollar sign
    '%',  # Percent
    '^',  # Caret
    '&',  # Ampersand
    '*',  # Asterisk
    '+',  # Plus
    '=',  # Equals
    '<',  # Less than
    '>',  # Greater than
    '`',  # Backtick
    '~'   # Tilde
]
    break_word_pattern = '[' + re.escape(''.join(break_word_characters)) + ']'
    
    for key, value in replacements.items():
        pattern = r'((?<=' + break_word_pattern + r')|^)' + key + r'((?=' + break_word_pattern + r')|$)'
        replaced_text = re.sub(pattern, value, replaced_text, 0)
    return replaced_text
