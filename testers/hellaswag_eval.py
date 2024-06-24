import ollama
import common
import logging
import pandas as pd
import logging
import datetime

import os

cert_path = '~/Emoji/Emojicrypt/ca-certificates.crt'
#os.environ["REQUESTS_CA_BUNDLE"]=cert_path
#os.environ["REQUESTS_CA_BUNDLE"]= os.path.expanduser(cert_path)

log_path = '~/Emoji/Emojicrypt/log/hellaswag_eval.log'
data_path = '~/Emoji/Emojicrypt/data/hellaswag-master/data/hellaswag_train.jsonl'


def hellaswag_complete_text(text, endings, client, model = 'llama3:8b'):
    promt_guidance = f"""I will give you 4 options to choose an ending to the following text, pick the most likely one. Think step by step, then write a line of the form "Answer: $ANSWER_NUMBER" at the end of your response. the text:\n"""
    answer = client.generate(model =model, prompt = promt_guidance + text + "...\n" + "Option 0: " + endings[0] + "\n" + "Option 1: " + endings[1] + "\n" + "Option 2: " + endings[2] + "\n" + "Option 3: " + endings[3])
    return answer["response"]

def test_hellaswag(number_of_tests_to_run, client, model = 'phi3:mini'):
    logger = common.init_logs(log_path,'h')
    logger.info(f"opening drop database\n")
    df = pd.read_json(data_path ,lines=True ,engine='pyarrow')
    original_prompt_correct_count = 0
    emoji_prompt_correct_count = 0
    answer_similarity = 0
    for index, row in df.iterrows():
        sentence = row['ctx']
        endings = row['endings']
        answer = row['label']
        logger.info(f"{index} sending querries\n")
        emoji_encrypt_text = common.emoji_encrypt_text(sentence,client, model)
        answer_original = common.extract_answer(hellaswag_complete_text(sentence, endings,client, model))          #Might want to split this so I can log the answers
        answer_emoji = common.extract_answer(hellaswag_complete_text(emoji_encrypt_text, endings,client, model))
        originial_correct = 1 if common.check_match(str(answer),str(answer_original),endings) else 0
        emoji_correct = 1 if common.check_match(str(answer),str(answer_emoji),endings) else 0
        original_prompt_correct_count += originial_correct
        emoji_prompt_correct_count += emoji_correct
        same_answer = 1 if common.check_match(str(originial_correct),str(emoji_correct)) else 0
        answer_similarity += same_answer
        logger.info(
            f"{index},{datetime.datetime.now()},model: {model}, sentence: {sentence},answer: {answer},original_answer: {answer_original},emoji_answer: {answer_emoji},same_answer: {same_answer}, ({originial_correct},{emoji_correct})"  
        )
        if index > number_of_tests_to_run:
            break

    return original_prompt_correct_count, emoji_prompt_correct_count, index

if __name__ == '__main__':
    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull('phi3:mini')
    logger = common.init_logs(log_path, 'h')
    original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_hellaswag(3,client)
    logger.info(f"Finished: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")

def main(number_of_test_to_run,client, models):
    logger = common.init_logs(log_path, 'h')
    model_results = {}
    for model in models:
        original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_hellaswag(number_of_test_to_run,client ,model)
        model_results[model + "_original"] = original_prompt_correct_count/test_count
        model_results[model + "_emoji"] = emoji_prompt_correct_count/test_count
        logger.info(f"Finished hellaswag: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")
    print(model_results)
    return model_results
