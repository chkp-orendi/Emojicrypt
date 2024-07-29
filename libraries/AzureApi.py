from openai import AzureOpenAI
import numpy as np
from numpy.linalg import norm
import os

os.environ["REQUESTS_CA_BUNDLE"]= r'C:\Users\orendi\Documents\EmojiCrypt\ca-certificates.crt'
log_path = '~/Emoji/Emojicrypt/log/embedding_eval.log'
data_path = '~/Emoji/Emojicrypt/data/embedding/embedding_test.xlsx'

API_KEY = "8838a1da61f047dab3916e1fd9d2023d"
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


def get_answer(text,model="gpt-4o-2024-05-13", temp = 0.0):
    answer = azure_client.chat.completions.create(
    model=model, messages=[{"role": "user", "content": text}], temperature=temp
)
    return answer.choices[0].message.content

def get_answer_with_histroy(messages, model="gpt-4o-2024-05-13", temp = 0.0, max_tokens = 400):
    answer = azure_client.chat.completions.create(
    model=model, messages=messages, temperature=temp
)
    return answer.choices[0].message.content

class AzureHelper:
    def __init__ (self, name, log_path, model, tempurature):
        self._name = name
        self._model = model
        self._log_path = log_path
        self._tempurature = tempurature
        self._client = AzureOpenAI(
            azure_endpoint=ENDPOINT,
            api_key=API_KEY,
            api_version="2023-07-01-preview"
        )
        self._prompt_list =[]
        self._chat_history =[]

    def update_chat_history(self, role, content):
        self._chat_history.append({
        'role': role,
        'content': content,
    })

    def send_query(self, text):
        self.update_chat_history('user', text)
        llm_response = self._client.chat.completions.create(model=self._model, messages=self._chat_history,temperature = self._tempurature, max_tokens=400)
        llm_response = get_answer_with_histroy(self._chat_history, self._model, self._tempurature)
        self.update_chat_history('assistant', llm_response)
        return llm_response

    def get_history(self):
        return self._chat_history

