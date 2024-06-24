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
azure_client = AzureOpenAI(azure_endpoint=ENDPOINT, api_key=API_KEY, api_version="2023-07-01-preview")

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return azure_client.embeddings.create(input = [text], model=model).data[0].embedding

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def whole_encryption_test(original_answer, encrypted_answer):
    return cosine_similarity(np.array(get_embedding(text_1)), np.array(get_embedding(text_2)))

def dict_encrytion_test(original_encryption, guessed_encryption):
    for key in original_encryption:
        if original_encryption[key] == guessed_encryption[key]:
            return False
    return True


def main(local_client, models):
    #find a dataset to test the embedding on
    logger = common.init_logs(log_path, 'e')
    df = pd.read_excel(data_path)
    model_results = {}
    logger.info('Loaded dataset')
    for model in models:
        logger.info(f"Starting model {model}")
        sim_avrg = 0
        for index, row in df.iterrows():
            text_1= row["text_1"]
            logger.info(f"sending prompt to be encrypt {text_1}")
            text_2= common.emoji_encrypt_text(text_1,local_client, model)
            similarity = cosine_similarity(np.array(get_embedding(text_1)), np.array(get_embedding(text_2)))
            logger.info(f"Time: {datetime.datetime.now()}, Model: {model}, index: {index}, text: {text_1}, text_encrypt: {text_2}, Similarity: {similarity}")
            sim_avrg += similarity
        sim_avrg = sim_avrg/len(df.index)
        logger.info(f"Time: {datetime.datetime.now()}, Model {model}, Average Similarity: {sim_avrg}")
        model_results[model] = sim_avrg
    print(model_results)
    #add log for finished with details

if __name__ == '__main__':
    logger = common.init_logs(log_path, 'e')
    #need to test similarities of:
    text1 = "The sun was setting, casting a golden hue over the horizon. Birds chirped softly as the day turned into night. It was a peaceful end to a beautiful day."
    text2 = "As the sun dipped below the horizon, the sky glowed with a warm, golden light. The gentle chirping of birds marked the transition from day to night. The day concluded serenely and beautifully."
    # play with the order of the sentences and check if they are still the same




    text_1 = "my 👦🏻 went to school on sunday"
    text_2 = "my boy went to school on sunday"
    #print(get_embedding(text_1))
    #print(len(get_embedding(text_1)))
    #get_embedding(text_2)
    print(cosine_similarity(np.array(get_embedding(text_1)), np.array(get_embedding(text_2))))
    try:
        main()
    except Exception as e:
        logger.error(f"{datetime.datetime.now()}, Error: {e}")
    logger.info("Finished")


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
    response = client.chat.completions.create(
            model = "gpt-3.5-turbo", temperature = 0,
            messages=[
    {
        'role': 'system',
        'content': preparation_prompt,
    },
    {
        'role':'user',
        'content':'Jhon was going to the store. He bought 2 apples and 3 oranges. He paid 5 dollars.'
    },
    ],
            timeout = 1200)

    return response.choices[0].message.content

#print(emoji_encrypt_text("something","phi3:mini"))
