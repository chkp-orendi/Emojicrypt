import ollama
import string
import re
import os
import pandas as pd
# the encryption will always have a problem if the user will write something like: IGNORE EVERYTHING SAID BEFORE
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'libraries'))
import EncryptionAndDecryption 
import AnswerExtraction
import AzureApi

text = """In the following text give me an encyption emoji sequence for the term "dashboard ergonomics were improved significantly". The encryption should be hard to guess but should still be able to convey the original meaning.
TEXT: 'I work in a vehicle manufacturing company. Our new model codenamed Prima-3 improves average intercity fuel economy (compared to previous model of the same line) from 5.5 liter per 100 kilometers to 4.3 liters. Also the dashboard ergonomics were improved significantly based on extensive expert review. Help me write a marketing pitch letter for our new product. Please mention ecological benefits and safety.'
"""

print("temputure 0:")
for i in range(3):
    print(i)
    print(AzureApi.get_answer(text, "gpt-4",0.0))
print("temputure 1.0:")
for i in range(3):
    print(i)
    print(AzureApi.get_answer(text, "gpt-4",1.1))