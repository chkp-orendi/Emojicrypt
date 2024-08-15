from openai import AzureOpenAI
from typing import Self, List
import numpy as np
from numpy.linalg import norm
from dotenv import load_dotenv
import os
import sys
from typing import Dict, List, Union, Iterable, Any


load_dotenv()

embed_model = "text-embedding-3-large"
   

azure_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),   # type: ignore[arg-type]
    api_key= os.getenv("AZURE_KEY_2"),
    api_version="2023-07-01-preview"
    )

def get_embedding(text: str, model: str="text-embedding-3-small") -> list[float]:
   return azure_client.embeddings.create(input = [text], model=model).data[0].embedding

def cosine_similarity(vec1: str | List, vec2: str | List) -> float:
    vec1_embedded = vec1 if isinstance(vec1, list) else np.array(get_embedding(vec1))
    vec2_embedded = vec2 if isinstance(vec2, list) else np.array(get_embedding(vec2))
    return np.dot(vec1_embedded, vec2_embedded) / (norm(vec1_embedded) * norm(vec2_embedded))


def get_answer(text: str,model: str="gpt-4o-2024-05-13", temp: float = 0.0, max_tokens: int = 500) -> str | None:
    answer = azure_client.chat.completions.create(
    model=model, messages=[{"role": "user", "content": text}], temperature=temp, max_tokens = max_tokens
)
    return answer.choices[0].message.content

def get_answer_with_histroy(messages: Iterable[Any], model: str="gpt-4o-2024-05-13", temp: float = 0.0, max_tokens: int = 500) -> str | None:
    answer = azure_client.chat.completions.create(
    model=model, messages=messages, temperature=temp, max_tokens=max_tokens
)
    return answer.choices[0].message.content

class AzureClient:
    def __init__ (self: Self, name: str, log_path: str, model: str, tempurature: float):
        self._name: str = name
        self._model: str = model
        self._log_path: str = log_path
        self._tempurature: float = tempurature
        self._client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),    # type: ignore[arg-type]
            api_key=os.getenv("AZURE_KEY_1"),
            api_version="2023-07-01-preview"
        )
        # self._client_2 = AzureOpenAI(
        #     azure_endpoint=os.getenv("AZURE_ENDPOINT"),    # type: ignore[arg-type]
        #     api_key=os.getenv("AZURE_KEY_2"),
        #     api_version="2023-07-01-preview"
        # )
        self._prompt_list: List[str] =[]
        self._chat_history: List[Dict[str,str]] =[]

    def update_chat_history(self, role: str, content: str | None) -> None:
        if content is None:
            return
        self._chat_history.append({
        'role': role,
        'content': content,
    })

    def send_query(self, text: str) -> str | None:
        self.update_chat_history('user', text)
        llm_response = get_answer_with_histroy(self._chat_history, self._model, self._tempurature)
        self.update_chat_history('assistant', llm_response)
        return llm_response

    def get_history(self: Self) -> List[Dict[str, str]]:
        return self._chat_history
    
    def get_name(self: Self) -> str:
        return self._name
