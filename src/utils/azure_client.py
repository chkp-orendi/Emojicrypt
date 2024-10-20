from openai import AzureOpenAI
from typing import Self, List
import numpy as np
from numpy.linalg import norm
from dotenv import load_dotenv
import os
import sys
from typing import Dict, List, Union, Iterable, Any
import time

load_dotenv()
   

MAX_TOKENS = int(os.getenv("MAX_TOKENS"))

class dynamic_azure_client:
    """class to use multiple azure clients. This would prevent crushes if one key is overused
    
    For list of models: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models
    
    Attributes:
        client_list (`List[AzureOpenAI]`): list of azure clients to use.
    
    """

    def __init__(self,client_list: List[AzureOpenAI]):
        self.client_list = client_list

    def get_embeddings(self,text: str, model: str="text-embedding-3-small") -> List[float]:
        for index, client in enumerate(self.client_list):
            try:
                return client.embeddings.create(input = [text], model=model).data[0].embedding
            except:
                print (f"key {index} failed")
                continue
    
    def get_answer(self,text: str,model: str="gpt-4o-2024-05-13", temp: float = 0.0,top_p: float = 1.0, max_tokens: int = 1000) -> str | None:
        while True:
            for index, client in enumerate(self.client_list):
                try:
                    answer = client.chat.completions.create(
                    model=model, messages=[{"role": "user", "content": text}], temperature=temp, top_p = top_p, max_tokens = max_tokens
                    )
                    return answer.choices[0].message.content
                
                except Exception as e:
                    print (f"key {index} failed: {e}")
                    continue
            time.sleep(10800)
        return "OVER USED ALL KEYS"
    
    def get_answer_with_histroy(self, messages: Iterable[Any], model: str="gpt-4o-2024-05-13", temp: float = 0.0, top_p: float = 1.0, max_tokens: int = 1000) -> str | None:
        while True:
            for index, client in enumerate(self.client_list):
                try:
                    return client.chat.completions.create(
                    model=model, messages=messages, temperature=temp, top_p = 1.0,max_tokens=max_tokens
                    ).choices[0].message.content
                except Exception as e:
                    print (f"key {index} failed: {e}")
                    continue
            time.sleep(10800)
    
    def get_json_with_histroy(self, messages: Iterable[Any], model: str="gpt-4o-2024-05-13", temp: float = 0.0, top_p: float = 1.0, max_tokens: int = 500) -> str | None:
        messages_copy = messages.copy()
        messages_copy.insert(0,{"role": "system", "content": "You are a helpful assistant designed to output JSON."})
        while True:
            for index, client in enumerate(self.client_list):
                try:
                    answer = client.chat.completions.create(
                    response_format={ "type": "json_object" },model=model, messages=messages, temperature=temp, top_p = 1.0, max_tokens=max_tokens
                    )
                    return answer.choices[0].message.content
                except Exception as e:
                    print("error", e)
                    print (f"key {index} failed")
                    continue
            time.sleep(10800)

        


azure_client_1 = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key= os.getenv("AZURE_KEY_1"),
    api_version="2023-07-01-preview"
    )

azure_client_2 = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key= os.getenv("AZURE_KEY_2"),
    api_version="2023-07-01-preview"
    )

azure_client_3 = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key= os.getenv("AZURE_KEY_3"),
    api_version="2023-07-01-preview"
    )


azure_client = dynamic_azure_client([azure_client_3,azure_client_1, azure_client_2])

def get_embedding(text: str, model: str="text-embedding-3-small") -> list[float]:
   """Args:
    - `param1 (str | List)`: text to convert.
    - `param1 str`: model to use for embedding.

    For list of embedding models see: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings-models
    
    Output:
    - cosine similarity between the two vectors    
    """
   return azure_client.get_embeddings(text = text, model=model)


def cosine_similarity(vec1: str | List[float], vec2: str | List[float]) -> float:
    """Inputs:
    - `param1 (str | List)`: text or vevctor i.e `list[float]`.
    - `param2 (str | List)`: text or vevctor i.e `list[float]`.
    
    Output:
    - cosine similarity between the two vectors
    """
    vec1_embedded = vec1 if isinstance(vec1, list) else np.array(get_embedding(vec1))
    vec2_embedded = vec2 if isinstance(vec2, list) else np.array(get_embedding(vec2))
    return np.dot(vec1_embedded, vec2_embedded) / (norm(vec1_embedded) * norm(vec2_embedded))


def get_answer(text: str,model: str="gpt-4o-2024-05-13", temp: float = 0.0, top_p: float = 1.0 ,max_tokens: int = 1000) -> str | None:

    """
    Get an answer **without history** from `model` on `text` with temperature `temp`, `top_p` and `max_tokens`.

    Args:
        text (`str`): text to be sent to model.
        model (`str`): model to use by LLM.
        temp (`float`): temperature to use by LLM.
        top_p (`float`): top_p to use by LLM.
        max_tokens (`int`): maximum tokens to use by LLM.

    Returns:
        answer: `string` from LLM

    """
    return azure_client.get_answer(
    model=model, text= text, temp=temp, top_p = top_p,max_tokens = max_tokens
    )


def get_answer_with_histroy(messages: Iterable[Any], model: str="gpt-4o-2024-05-13", temp: float = 0.0, max_tokens: int = 1000) -> str | None:
    """
    Get an answer **with history** from `model` on `messages` with temperature `temp`, `top_p` and `max_tokens`.

    Args:
        messages (`Iterable[Any]`): messages should be list of {'role': role, 'content': content}
        model (`str`): model to use by LLM.
        temp (`float`): temperature to use by LLM.
        top_p (`float`): top_p to use by LLM.
        max_tokens (`int`): maximum tokens to use by LLM.

    Returns:
        answer: `string` from LLM

    """
    return azure_client.get_answer_with_histroy(
    model=model, messages=messages, temp=temp, max_tokens=max_tokens
)



def get_json_with_histroy(messages: Iterable[Any], model: str="gpt-4o-2024-05-13", temp: float = 0.0, top_p: float = 1.0, max_tokens: int = MAX_TOKENS) -> str | None:
    return azure_client.get_json_with_histroy(messages=messages, model=model, temp=temp, top_p=top_p, max_tokens=max_tokens)


class AzureClient:
    """
Class to handle azure client when chat histroy is needed.
    """


    def __init__ (self: Self, name: str, log_path: str, model: str, tempurature: float):
        self._name: str = name
        self._model: str = model
        self._log_path: str = log_path
        self._tempurature: float = tempurature
        self._clients = dynamic_azure_client([azure_client_1,azure_client_2])

        self._prompt_list: List[str] =[]
        self._chat_history: List[Dict[str,str]] =[]

    def update_chat_history(self, role: str, content: str | None) -> None:
        if content is None:
            return
        self._chat_history.append({
        'role': role,
        'content': content,
    })

    def send_query(self, text: str, max_tokens = MAX_TOKENS) -> str | None:
        self.update_chat_history('user', text)
        llm_response = get_answer_with_histroy(self._chat_history, self._model, self._tempurature, max_tokens=max_tokens)
        self.update_chat_history('assistant', llm_response)
        return llm_response


    def get_history(self: Self) -> List[Dict[str, str]]:
        return self._chat_history
    
    def get_name(self: Self) -> str:
        return self._name


# print(get_answer("What is the capital of France?"))