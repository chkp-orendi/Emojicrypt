import pandas as pd
import re
import common
import embedding_eval
import ollama
import logging
import datetime
import os

# This test is not eligible since the answers are open and contain names. So without the encryption part there is no possible way to test if the answer is correct.



log_path = '~/Emoji/Emojicrypt/log/drop_eval.log'
data_path = '~/Emoji/Emojicrypt/data/drop/train-00000-of-00001.parquet'


def get_prompt_format(passage,question):
    prompt =f"""
    Passage:{passage}
    Question:{question}
    """
    return prompt

def get_answer(prompt, client, model="phi3:mini"):
    pre_prompt ="""You will be asked to read a passage and answer a question.\n"""
    
    pre_prompt += f"""Think step by step, then write a line of the form "Answer: $ANSWER" at the end of your response.\n"""
    answer = client.generate(model =model, prompt = pre_prompt + prompt)
    return answer["response"]


def eval_drop(numberof_tests_to_run, client, model = "phi3:mini"):
    drop_logger = logging.getLogger("drop")
    drop_logger.info(f"opening drop database\n")
    df = pd.read_parquet(data_path)
    original_prompt_correct_count = 0
    encrypted_prompt_correct_count = 0
    answer_similarity = 0
    embedded_similarity_sum = 0
    percentage_words_replaced_avrage =0

    for index, row in df.iterrows():
        try:
            print(f"drop - {model} - {index}")
            passage = row["passage"]
            question = row["question"]
            answers_spans = row["answers_spans"]["spans"]

            # Get encryption dictionary for prompt and encrypt it and get answers
            prompt_encryption_dict = common.get_encryption_dict(passage,client, model)
            encrypted_passage, percentage_words_replaced = common.encrypt_text(passage,prompt_encryption_dict)
            encrypted_question = common.encrypt_text(question,prompt_encryption_dict)
            #encrypt_answer = common.encrypt_text(answers_spans,prompt_encryption_dict)

            original_prompt_answer = get_answer(get_prompt_format(passage,question), client, model)
            encrypted_prompt_answer = get_answer(get_prompt_format(encrypted_passage,encrypted_question), client, model)
            original_prompt_extracted_answer = common.extract_answer(original_prompt_answer)
            encrypted_prompt_extracted_answer = common.extract_answer(encrypted_prompt_answer)
            decrypted_encrypted_answer = common.decrypt_text(encrypted_prompt_answer,prompt_encryption_dict)

            # Compare answers
            original_prompt_correctness = 1 if common.check_match(str(original_prompt_answer),str(answers_spans)) else 0
            encrypted_prompt_correctness = 1 if common.check_match(str(decrypted_encrypted_answer),str(answers_spans)) else 0
            same_answer = 1 if common.check_match(str(original_prompt_answer),str(decrypted_encrypted_answer)) else 0
            answer_similarity += same_answer
            original_prompt_correct_count += original_prompt_correctness
            encrypted_prompt_correct_count += encrypted_prompt_correctness

            embedded_similarity = embedding_eval.cosine_similarity(embedding_eval.get_embedding(encrypted_passage),embedding_eval.get_embedding(passage))
            embedded_similarity_sum += embedded_similarity
            percentage_words_replaced_avrage += percentage_words_replaced
            drop_logger.info(
    f"""@@@@
    {datetime.datetime.now()}, model: {model}, index: {index}
    passage: {passage}
    question: {question}
    answer: {answers_spans}

    prompt_encryption_dict: {prompt_encryption_dict}

    encrypted_passage: {encrypted_passage}
    encrypted_question: {encrypted_question}
    original_prompt_answer: {original_prompt_answer}
    encrypted_prompt_answer: {encrypted_prompt_answer}
    original_prompt_extracted_answer: {original_prompt_extracted_answer}
    encrypted_prompt_extracted_answer: {encrypted_prompt_extracted_answer}
    decrypted_encrypted_answer: {decrypted_encrypted_answer}
    (original_prompt_correctness,encrypted_prompt_correctness): ({original_prompt_correctness},{encrypted_prompt_correctness})
    similar_answer: {same_answer}
    Cosine similarity- passage: {embedded_similarity}
    percentage_words_replaced: {percentage_words_replaced}
    """
            )
        except Exception as e:
            drop_logger.error(f"ERROE: {e}\nAT INDEX: {index}\nAT MODEL: {model}\nAT TIME: {datetime.datetime.now()}")
        if index >= numberof_tests_to_run:
            break
    return original_prompt_correct_count , encrypted_prompt_correct_count, answer_similarity, embedded_similarity_sum,percentage_words_replaced_avrage, index+1

if __name__ == '__main__':
    client = ollama.Client(host='http://172.23.81.3:11434')
    drop_logger = common.init_logs(log_path, 'w')
    client.pull('phi3:mini')
    original_prompt_correct_count , emoji_prompt_correct_count, test_count = eval_drop(-1,client)

def main(number_of_test_to_run, client, models):
    drop_logger = logging.getLogger("drop")
    drop_logger.info(f"Starting drop_eval.py\n")
    model_results = {}
    for model in models:
        original_prompt_correct_count , emoji_prompt_correct_count, answer_similarity, avrage_embedding_similarity,percentage_words_replaced_avrage, test_count = eval_drop(number_of_test_to_run,client ,model)
        model_results[model + "_original"] = original_prompt_correct_count/test_count
        model_results[model + "_encrypted"] = emoji_prompt_correct_count/test_count
        model_results[model + "_answer_similarity"] = answer_similarity/test_count
        model_results[model + "_avrage_embedding_similarity"] = avrage_embedding_similarity/test_count
        model_results[model + "percentage_words_replaced_avrage"] = percentage_words_replaced_avrage/test_count
        drop_logger.info(
            f"""Finished drop with {model} with {test_count} tests:
{model}"_original": {model_results[model + "_original"]}
{model}"_encrypted": {model_results[model + "_encrypted"]}
{model}"_answer_similarity": {model_results[model + "_answer_similarity"]}
{model}"_avrage_embedding_similarity": {model_results[model + "_avrage_embedding_similarity"]}
{model}"percentage_words_replaced_avrage": {model_results[model + "percentage_words_replaced_avrage"]}%
"""
)
        main_logger = logging.getLogger("main")
        main_logger.info(
            f"""Finished drop with {model} with {test_count} tests:
{model}"_original": {model_results[model + "_original"]}
{model}"_encrypted": {model_results[model + "_encrypted"]}
{model}"_answer_similarity": {model_results[model + "_answer_similarity"]}
{model}"_avrage_embedding_similarity": {model_results[model + "_avrage_embedding_similarity"]}
{model}"percentage_words_replaced_avrage": {model_results[model + "percentage_words_replaced_avrage"]}%
"""
)
    print(model_results)
    return model_results
