from dotenv import load_dotenv 
import os
import sys
import statistics
import numpy as np
import json

load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.utils.azure_client import get_answer


import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize

# Download necessary resources
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

def is_linking_word(word):
    # Tokenize the input word and get its POS tag
    pos = pos_tag([word])[0][1]
    
    # Linking words can be coordinating conjunctions (CC), subordinating conjunctions (IN),
    # or prepositions (IN), or any other linking-related tags
    linking_tags = {'CC', 'IN'}
    
    return pos in linking_tags

# Example usage:
print(is_linking_word("and"))  # True
print(is_linking_word("cat"))  # False
