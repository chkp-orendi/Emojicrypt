from openai import AzureOpenAI
import numpy as np
from numpy.linalg import norm
import logging
import pandas as pd
import datetime
import EncryptionAndDecryption
import os

os.environ["REQUESTS_CA_BUNDLE"]= r'C:\Users\orendi\Documents\EmojiCrypt\ca-certificates.crt'
log_path = '~/Emoji/Emojicrypt/log/embedding_eval.log'
data_path = '~/Emoji/Emojicrypt/data/embedding/embedding_test.xlsx'

API_KEY = "95787a606b6b4d41800ec9ff2b6ddcb8"
ENDPOINT = "https://staging-dev-openai.azure-api.net/openai-gw-proxy-dev/"
embed_model = "text-embedding-3-large"
azure_client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version="2023-07-01-preview"
    )

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return azure_client.embeddings.create(input = [text], model=model).data[0].embedding

def cosine_similarity(vec1, vec2):
    if (type(vec1) == str):
        try:
            vec1 = np.array(get_embedding(vec1))
            vec2 = np.array(get_embedding(vec2))
        except:
            print("Error in embedding")
            return -1
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def get_answer(text,model, temp = 0.0):
    answer = azure_client.chat.completions.create(
    model=model, messages=[{"role": "user", "content": text}], temperature=temp
)
    return answer.choices[0].message.content

def get_answer_with_histroy(messages, model, temp = 0.0):
    answer = azure_client.chat.completions.create(
    model=model, messages=messages, temperature=temp
)
    return answer.choices[0].message.content

