import ollama
import common
import logging
import pandas as pd
import logging
import datetime

import os

# class _OllamaCommon(BaseLanguageModel):
#    base_url: str = os.getenv('OLLAMA_SERVER_URL', "http://172.23.81.3:11434")

logger = logging.getLogger(__name__)
def init_logs():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='C:/Users/orendi/Documents/EmojiCrypt/log/hellaswag_eval.log', level=logging.INFO)
    logger.info('Started hellaswag_eval.py')

def hellaswag_complete_text(text, endings, model = 'llama3:8b'):
    promt_guidance = f"""I will give you 4 options to choose an ending to the following text, pick the most likely one. Think step by step, then write a line of the form "Answer: $ANSWER_NUMBER" at the end of your response. the text:\n"""
    answer = ollama.generate(model =model, prompt = promt_guidance + text + "...\n" + "Option 0: " + endings[0] + "\n" + "Option 1: " + endings[1] + "\n" + "Option 2: " + endings[2] + "\n" + "Option 3: " + endings[3])
    return answer["response"]

def test_hellaswag(number_of_tests_to_run, model = 'phi3:mini'):
    logger.info(f"opening drop database\n")
    df = pd.read_json(r"C:\Users\orendi\Documents\EmojiCrypt\data\hellaswag-master\data\hellaswag_train.jsonl",lines=True ,engine='pyarrow')
    original_prompt_correct_count = 0
    emoji_prompt_correct_count = 0
    for index, row in df.iterrows():
        sentence = row['ctx']
        endings = row['endings']
        answer = row['label']
        logger.info(f"{index} sending querries\n")
        emoji_encrypt_text = common.emoji_encrypt_text(sentence, model)
        answer_original = common.extract_answer(hellaswag_complete_text(sentence, endings, model))          #Might want to split this so I can log the answers
        answer_emoji = common.extract_answer(hellaswag_complete_text(emoji_encrypt_text, endings, model))
        originial_correct = 1 if common.check_match(str(answer),str(answer_original),endings) else 0
        emoji_correct = 1 if common.check_match(str(answer),str(answer_emoji),endings) else 0
        original_prompt_correct_count += originial_correct
        emoji_prompt_correct_count += emoji_correct
        
        logger.info(
            f"{index},{datetime.datetime.now()},model: {model}, sentence: {sentence},answer: {answer},answer_original: {answer_original},answer_emoji: {answer_emoji},({originial_correct},{emoji_correct})"  
        )
        originial_correct = 1 if common.check_match(str(answer),str(answer_original)) else 0
        emoji_correct = 1 if common.check_match(str(answer),str(answer_emoji)) else 0
        if index > number_of_tests_to_run:
            break

    return original_prompt_correct_count, emoji_prompt_correct_count, index

if __name__ == '__main__':
    init_logs()
    original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_hellaswag(3)
    logger.info(f"Finished: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")

def main(number_of_test_to_run,models):
    init_logs()
    model_results = {}
    for model in models:
        original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_hellaswag(number_of_test_to_run, model)
        model_results[model + "_original"] = original_prompt_correct_count/test_count
        model_results[model + "_emoji"] = emoji_prompt_correct_count/test_count
        logger.info(f"Finished hellaswag: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")
    print(model_results)