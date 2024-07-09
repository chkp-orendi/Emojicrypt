from openai import AzureOpenAI
import numpy as np
from numpy.linalg import norm
import logging
import pandas as pd
import datetime
import common
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
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def compare_text_embedding_similarity(text_1, text_2):
    return cosine_similarity(np.array(get_embedding(text_1)), np.array(get_embedding(text_2)))


def get_answer(text,model):
    answer = azure_client.chat.completions.create(
    model=model, messages=[{"role": "user", "content": text}]
)
    return answer.choices[0].message.content

