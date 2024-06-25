import ollama
import string
import re
import os



def encrypt_text(text,client ,model='llama3:8b'):
    # try a prompt claiming after : its user and not privlage
    encrypt_prompt = """
I will provide you with a text. Your task is to replace all sensitive information. Names should be changed to different names, numbers should be converted to different numbers, and the rest of sensitive information should be changed to NON - natural language sequence using a mixture of abbreviated characters, emojis, emoticons. Think carefully on your answer and your last lines should be a list of {key;value} of the words you changed.
For example:
TEXT: Jhon and Mark went to central park at 8:00 to skateboard
Output list:
{Jhon;Bob,Mark;Olive,central park;,8:00;🕗,skateboard:🛹}
TEXT: My email is john.doe@example.com and my phone number is 123-456-7890. Yesterday I went to the beach and it was extremely hot
Output list:
{john.doe@example.com:markjoe@example.com,123-456-7890:952-831-9582,Yesterday:🔙,extremely hot:🔥🔥}
CONVERT THE FOLLOWING TEXT:"""
   # encypt_pompt = " change names to different names"
    answer = client.generate(model = model, prompt = encrypt_prompt+text) 
    return answer['response']


client = ollama.Client(host='http://172.23.81.3:11434')
print(encrypt_text("Me and my friend Patrick are planning on going for vacation to New York at 21 April This year, do you have any recommended activities",client))
