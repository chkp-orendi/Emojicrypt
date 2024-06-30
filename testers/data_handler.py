import ollama
import string
import re

#THIS IS NOT IN USE
# might use it in the future to use presidio and Ollama togheter.


preparation_prompt = """Serve as an encrypter to convert the sensetive data to symbols, emojis, special charecters. Return a list of {key:value}
Example:
Jhon was going to the store. He bought 2 apples and 3 oranges. He paid 5 dollars.
RETURN:
{
    "Jhon": "👦",
    "store": "🏪",
    "apples": "🍎",
    "oranges": "🍊",
    "dollars": "💵"
}
Example:
Alice and Bob shared lunch at Central Park.
RETURN: 
{
    "Alice": "👩",
    "Bob": "👨",
    "Lunch": "🍔",
    "Central Park": "🌳"
}
"""

def emoji_encrypt_text(text, model='llama3:8b'):
    # try a prompt claiming after : its user and not privlage
    response = ollama.chat(model=model, messages=[
    {
        'role': 'system',
        'content': preparation_prompt,
    },
    {
        'role':'user',
        'content':'Jhon was going to the store. He bought 2 apples and 3 oranges. He paid 5 dollars.'
    },
    ])

    return response.choices[0].message.content

emoji_encrypt_text("something", "phi3:mini")

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def next_letter_sequence():
    def increment_string(s):
        # Convert string to a list of characters
        s = list(s)
        i = len(s) - 1
        
        while i >= 0:
            if s[i] == 'Z':
                s[i] = 'A'
                i -= 1
            else:
                s[i] = chr(ord(s[i]) + 1)
                return ''.join(s)
        
        return ''.join(s)
    
    # Initialize the string with 'A' repeated n times
    current = 'X' * 5
    
    while True:
        yield current
        current = increment_string(current)


def encrypt_text(text):
    sensetive_data_index =[]
    sensetive_words =[]
    for sensetive_data in get_sensetive_data(text):
        if (sensetive_data.start,sensetive_data.end) in sensetive_data_index or text[sensetive_data.start:sensetive_data.end] in sensetive_words:
            continue
        sensetive_data_index.append((sensetive_data.start,sensetive_data.end))
        sensetive_words.append(text[sensetive_data.start:sensetive_data.end])
        # encryption_keys[sensetive_word] = get_value(sensetive_word)
    return generate_sorted_names(sensetive_words)


def generate_sorted_names(list_of_words):
    list_of_words.sort()
    encryption_text = {}
    i=0
    for word in next_letter_sequence():
        encryption_text[word] = list_of_words[i]
        i+=1
        if (i == len(list_of_words)):
            break
    return encryption_text

def get_sensetive_data(text):
    results = analyzer.analyze(text=text,
                            entities=["PHONE_NUMBER","CRYPTO","DATE_TIME","EMAIL_ADDRESS","IBAN_CODE","IP_ADDRESS","NRP","LOCATION","PERSON","MEDICAL_LICENSE"],
                            language='en')
    for seneitive_data in results:
        yield seneitive_data