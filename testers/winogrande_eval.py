import logging
import ollama
import pandas as pd
import datetime
import common
import os

log_path = '~/Emoji/Emojicrypt/log/winogrande_eval.log'
data_path = '~/Emoji/Emojicrypt/data/winogrande_1.1/train_xs.jsonl'


def winogrande_get_answer(text, option_1, option_2,client,  model = 'llama3:8b'):
    promt_guidance = f"""Complete the blank from the 2 options. Think step by step, then write a line of the form "Answer: $ANSWER_NUMBER" at the end of your response.\nText: """
    answer = client.generate(model =model, prompt = promt_guidance + text + "...\n" + "Option 1: " + option_1 + "\n" + "Option 2: " + option_2 + "\n")
    return answer["response"]


def test_winogrande(number_of_tests_to_run,client, model = 'phi3:mini'):
    logger = common.init_logs(log_path,'w')
    original_prompt_correct_count = 0
    emoji_prompt_correct_count = 0
    logger.info(f"opening drop database\n")
    df = pd.read_json(data_path, lines=True)
    answer_similarity = 0

    for index, row in df.iterrows():
        sentence = row['sentence']
        option_1 = row['option1']
        option_2 = row['option2']
        answer = row['answer']
        logger.info(f"sending querries {index}\n")
        answer_original = common.extract_answer(winogrande_get_answer(sentence, option_1, option_2, client, model))
        answer_emoji = common.extract_answer(winogrande_get_answer(common.emoji_encrypt_text(sentence,client), option_1, option_2, client, model))
        originial_correct = 1 if common.check_match(str(answer),str(answer_original), [option_1,option_2]) else 0
        emoji_correct = 1 if common.check_match(str(answer),str(answer_emoji), [option_1,option_2]) else 0
        original_prompt_correct_count += originial_correct
        emoji_prompt_correct_count += emoji_correct
        same_answer = 1 if common.check_match(str(originial_correct),str(emoji_correct)) else 0
        answer_similarity += same_answer

        logger.info(
            f"{datetime.datetime.now()},model: {model}, index: {index}, sentence: {sentence},option_1: {option_1},option_2: {option_2},answer: {answer},answer_original: {answer_original},answer_emoji: {answer_emoji}, same_answer: {same_answer}, ({originial_correct},{emoji_correct})"  
        )

        if index > number_of_tests_to_run:
            break
    return original_prompt_correct_count , emoji_prompt_correct_count, index


if __name__ == '__main__':
    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull("phi3:mini")
    logger = common.init_logs(log_path, 'w')
    original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_winogrande(3,client)
    logger.info(f"Finished: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")

def main(number_of_test_to_run,client, models):
    logger = common.init_logs(log_path, 'w')
    model_results = {}
    for model in models:
        original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_winogrande(number_of_test_to_run, client, model)
        model_results[model + "_original"] = original_prompt_correct_count/test_count
        model_results[model + "_emoji"] = emoji_prompt_correct_count/test_count
        logger.info(f"Finished winogrande: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")
    print(model_results)
    return model_results
