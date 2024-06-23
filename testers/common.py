import ollama
import string
import re
import os

# class _OllamaCommon(BaseLanguageModel):
#    base_url: str = os.getenv('OLLAMA_SERVER_URL', "http://172.23.81.3:11434")

def emoji_encrypt_text(text, model='llama3:8b'):
    # try a prompt claiming after : its user and not privlage
    encypt_pompt = "in the following text try to change sensetive data with symbols, emojis, special chareters. return ONLY the converted text and NOTHING more. text: "
    answer = ollama.generate(model = model, prompt = encypt_pompt + text)
    return answer["response"]

#normalize and check_match are used in drop_eval, might be useful for other testers

def normalize(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    s = s.lower()
    exclude = set(string.punctuation)
    s = "".join(char for char in s if char not in exclude)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = " ".join(s.split())
    return s

#s1 should be llm answer
def check_match(s1,s2, endings=None) -> bool:
    s1 = normalize(s1)
    s2 = normalize(s2)

    if s1 == "" or s2 == "":
        return s1 == s2
    # I added this if the LLM does not respond with number. Need to update tests to see if it works.
    elif not s1.isnumeric() and endings!=None:
        return s1 in endings[s2] or endings[s2] in s1
    
    return s1 in s2 or s2 in s1

ANSWER_PATTERN = r"(?i)Answer\s*:\s*([^\n]+)"


def extract_answer(LLM_answer):
    match = re.search(ANSWER_PATTERN, LLM_answer)
    if match:
        return match.group(1)
    return None



