import pandas as pd
import re
import common
import ollama
import logging
import datetime
import os

# This test is not eligible since the answers are open and contain names. So without the encryption part there is no possible way to test if the answer is correct.



log_path = '~/Emoji/Emojicrypt/log/drop_eval.log'
data_path = '~/Emoji/Emojicrypt/data/drop/train-00000-of-00001.parquet'



def get_prompt_format(passage,question):
    # the prompt format was taken from simple-evals/drop_eval.py. they put examples that will bring better result but the number of tokens are tripled.
    prompt ="""You will be asked to read a passage and answer a question.\n"""
    
    prompt += f"""Think step by step, then write a line of the form "Answer: $ANSWER" at the end of your response.
    Passage: {passage}
    Question: {question}
    """
    return prompt



def get_answer(prompt, client, model="phi3:mini"):
    answer = client.generate(model =model, prompt = prompt)
    return common.extract_answer(answer["response"])



def eval_drop(numberof_tests_to_run, client, model = "phi3:mini"):
    logger = common.init_logs(log_path,'d')
    logger.info(f"opening drop database\n")
    df = pd.read_parquet(data_path)
    original_prompt_correct_count = 0
    emoji_prompt_correct_count = 0
    answer_similarity = 0
    for index, row in df.iterrows():
        passage = row["passage"]
        question = row["question"]
        answers_spans = row["answers_spans"]["spans"]
        prompt = get_prompt_format(passage,question)
        logger.info(f"{index} sending querries\n")
        # encrypting the passage and question and then send to passage and question format.
        emoji_prompt = get_prompt_format(common.emoji_encrypt_text(passage, client,model),common.emoji_encrypt_text(question,client,model))
        original_answer = get_answer(prompt, client, model)
        emoji_answer = get_answer(emoji_prompt, client, model)
        originial_correct = 1 if common.check_match(str(original_answer),str(answers_spans)) else 0
        emoji_correct = 1 if common.check_match(str(emoji_answer),str(answers_spans)) else 0
        same_answer = 1 if common.check_match(str(originial_correct),str(emoji_correct)) else 0
        answer_similarity += same_answer
        original_prompt_correct_count += originial_correct
        emoji_prompt_correct_count += emoji_correct
        logger.info(
            f"{index},{datetime.datetime.now()},model: {model}, passage: {passage},question: {question},answer_spans: {answers_spans},original_answer: {original_answer},emoji_answer: {emoji_answer},same_answer: {same_answer}, ({originial_correct},{emoji_correct})"  
        )
        if index > numberof_tests_to_run:
            break
    return original_prompt_correct_count , emoji_prompt_correct_count, index

if __name__ == '__main__':
    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull('phi3:mini')
    logger = common.init_logs(log_path, 'd')
    original_prompt_correct_count , emoji_prompt_correct_count, test_count = eval_drop(3,client)
    logger.info(f"Finished: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")

def main(number_of_test_to_run, client, models):
    logger = common.init_logs(log_path, 'd')
    model_results = {}
    for model in models:
        original_prompt_correct_count , emoji_prompt_correct_count, test_count = eval_drop(number_of_test_to_run,client ,model)
        model_results[model + "_original"] = original_prompt_correct_count/test_count
        model_results[model + "_emoji"] = emoji_prompt_correct_count/test_count
        logger.info(f"Finished drop: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")
    print(model_results)
    return model_results
