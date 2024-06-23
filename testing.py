import ollama
import string
import re
import os

def emoji_encrypt_text(text, model='llama3:8b'):
    # try a prompt claiming after : its user and not privlage
    encypt_pompt = "in the following text try to change sensetive data with symbols, emojis, special chareters. return ONLY the converted text and NOTHING more. text: "
    answer = ollama.generate(model = model, prompt = encypt_pompt + text)
    return answer["response"]

for i in range(100):
    print(emoji_encrypt_text("tell me a long and intresting story about the number " + str(i)))