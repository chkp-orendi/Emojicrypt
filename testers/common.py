import ollama
import string
import re
import os
import logging

log_path = '~/Emoji/Emojicrypt/log/wrong_format_encryption.log'


## try prompt where we ask for a list with details
#{ 
# key:value - explaination
# }

def get_encryption_dict(text, client ,model='llama3:8b'):
    enc_logger = logging.getLogger('wrong format encryption')
    encryption_dict = {}
    encrypt_prompt = """
Convert the following text to a list of the format {key1;value1,key2;value2...}  based on these rules:
1. Replace names with random, unrelated names that do not appear anywhere else in the text. Maintain GENDER and ethnic of the name.
2. Replace numbers with random numbers of a similar magnitude to maintain plausibility but do not appear anywhere else in the text. If the context involves a sequence of numbers, ensure that the new, random numbers preserve the original ordering in terms of relative size. For instance, if a sequence of numbers increases or decreases, the transformed sequence should reflect the same pattern.
Examples:
Original: "His salary increased from 50,000 to 70,000 last year." --> Transformed: "His salary increased from 48,000 to 68,000 last year."
Original: "She ran 5 kilometers in 25 minutes." --> Transformed: "She ran 4 kilometers in 20 minutes."
3. Replace dates and times into emojis that reflect the general period or characteristic of the original text. Use a combination of emojis to represent more abstract concepts like months or years. (e.g 8:00;🕗,last year;🔙🔙📅,July;🔥📅).
4. Replace names of places with emojis that represent the primary attribute or the essence of the location. Select emojis that closely relate to the activities, climate, or notable features of these places. For example, {Central Park;🌳🌳,"beach;🏖️  ,library;📚}
5. Convert sensitive information such as email addresses, phone numbers, and social security numbers into realistic-looking but completely unrelated sequences. Use formats typical for the data type being transformed to ensure the result seems plausible. For email addresses, maintain a structure resembling [name]@[domain].com; for phone numbers, use a believable area code followed by random digits; and for social security numbers, format them as three digits, followed by two, then four digits, mimicking the standard format.
For example:
Original: "My email is john.doe@example.com." --> Transformed: "My email is alan.smith@website.com."
Original: "Her phone number is 123-456-7890." --> Transformed: "Her phone number is 987-654-3210."
Original: "His Social Security Number is 987-65-4320." --> Transformed: "His Social Security Number is 123-45-6789."
6. If the text does not contain any sensitive information, do not alter it.


Here are examples how to use all the rules to make a list to the text with the format {key1;value1,key2;value2...}. Make sure you use ; and not ; to split between key;value.

EXAMPLES:
TEXT: Jhon and Mark went to central park at 8:00 to skateboard
Output list:
{Jhon;Bob,Mark;Olive,central park;8:00;🕗,skateboard:🛹}
TEXT: My email is john.doe@example.com and my phone number is 123-456-7890. Yesterday I went to the beach and it was extremely hot
Output list:
{john.doe@example.com;markjoe@example.com,123-456-7890;952-831-9582,Yesterday;🔙,extremely hot;🔥🔥}
TEXT: Jhon got 100 at the test and Mark got 95, their avrage is 97.5
Output list:
{Jhon;Bob,Mark;Olive,100;98,95;97,97.5;}

Now convert the following text:"""
    answer = client.generate(model = model, prompt = encrypt_prompt + text)
    model_encryption = re.findall(r'\{[^{}]*\}',answer["response"])
    if len(model_encryption)>1:
         model_encryption=model_encryption[1]
    else:
        model_encryption =model_encryption[0]
    if (len(model_encryption)<3):
        return "NO VALID ANSWER"
    
    problematic_items = []
    for item in model_encryption[1:-1].split(","):
        try:
            key, value = item.split(";")
        except:
            try:
                key, value = item.split(":")
            except:
                problematic_items.append(item)
                continue
        encryption_dict[key]=value
    
    if (len(problematic_items)>0):
        enc_logger.info(
f"""MODEL: {model}
TEXT: {text}
MODEL ENCRYPTION: {model_encryption}
"""
        )
        for item in problematic_items:
            enc_logger.info(
f"""ITEM: {item}
"""
        )
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
