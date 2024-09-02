
import string
import re
import os
import logging
from typing import Optional
import emoji

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
    '~',  # Tilde
    '\"',  # Double quote
]

break_word_characters_without_bracket = break_word_characters.copy()
break_word_characters_without_bracket.remove(')')
break_word_characters_without_bracket.remove('(')
break_word_characters_without_bracket.remove('[')
break_word_characters_without_bracket.remove(']')

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
# extract_answer if in the prompt it was requested for format $Context: answer
# def extract_context(LLM_answer: str) -> Optional[str]:
#     ANSWER_PATTERN = r"\$Context:\s*(.*?)(?:\n\n|\Z)"
#     match = re.search(ANSWER_PATTERN, LLM_answer)
#     if match:
#         return match.group(1)
#     return None


def extract_context(text: str):
    match = re.search(r'Context:\s*(.*?)(?:\n|\Z)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

# extract_answer if in the prompt it was requested for format $Question: answer
def extract_question(LLM_answer: str) -> Optional[str]:
    ANSWER_PATTERN = r"Question:\s*(.*?)(?:\n|\Z)"
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

def fix_dict_ending(dictonary_str: str) -> str:
    """
If dictonary string is too long and was cut off for some reason (i.e max tokens)
Correct the ending, remove sequence after ',' and add ] at the end
"""
    return dictonary_str[:dictonary_str.rfind(",")] + "]"


# dict is in the foramt for: $Dict:  [word1:key1,words2:key2,...]
def extract_dict(LLM_answer):
        ANSWER_PATTERN = r'\$Dict:\s*\[\s*((?:.|\n)+)\s*\]'
        LLM_answer_fixed = fix_dict_ending(LLM_answer)
        # ANSWER_PATTERN = r'\$Dict:\s*\[(?:\s*[^:\[\],]+:[^:\[\],]+\s*,)*\s*[^:\[\],]+:[^:\[\],]+\s*\]'
        answer_list = re.findall(ANSWER_PATTERN, LLM_answer_fixed)
        if len(answer_list) >= 1:
            answer_list = answer_list[-1]  # return last occurrence of pattern.
        else:
            return {}
        
        words_replacements = {}
        answer_list = answer_list.replace("$Dict:", "").strip("[] \"")
        for item in answer_list.split(","):
            splited_item = item.split(":")
            if len(splited_item) !=2:
                print("INVALID ITEM")
                print(splited_item)
                print(LLM_answer_fixed)
                continue
            key = item.split(":")[0].strip(''.join(break_word_characters_without_bracket))
            value = item.split(":")[1].strip(''.join(break_word_characters_without_bracket))
            if key not in words_replacements.keys() and value not in words_replacements.values():
                words_replacements[key] = value
        return words_replacements

def extract_number(text: str) -> float:
    # Use regular expression to find all numbers in the text
    pattern = r'\$ANSWER: (-?\d+\.\d+)' #|-?\d+

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
    replaced_text = text.lower()
    break_word_pattern = '[' + re.escape(''.join(break_word_characters_without_bracket)) + ']'
    
    for key, value in sorted(replacements.items(),key=lambda x: len(x[0]), reverse=True):
        pattern = r'((?<=' + break_word_pattern + r')|^)' + re.escape(key.lower()) + r'((?=' + break_word_pattern + r')|$)'
        replaced_text = re.sub(pattern, value, replaced_text, 0)
    return replaced_text



def contains_emoji(word):
    return any(char in emoji.EMOJI_DATA for char in word)

def unwanted_emoji_counter(text: str, dict_s_t_e: dict):
    """
    count number of emoji not in the dictionary.
    expected to get dictionary string to emoji
    """
    text_copy = text
    for value in dict_s_t_e.values():
        text_copy = text_copy.replace(value, '') # remove emoji from text 
    
    count = 0
    for word in text_copy.split():
        if contains_emoji(word):
            count += 1
    return count
