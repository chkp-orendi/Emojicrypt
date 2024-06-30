import logging
import ollama
import pandas as pd
import datetime
import common
import embedding_eval

import os

log_path = '~/Emoji/Emojicrypt/log/winogrande_eval.log'
data_path = '~/Emoji/Emojicrypt/data/winogrande_1.1/train_xs.jsonl'


def winogrande_get_answer(text, option_1, option_2,client,  model = 'llama3:8b'):
    promt_guidance = f"""Complete the blank from the 2 options. Think step by step, then write a line of the form "Answer: $ANSWER_NUMBER" at the end of your response.\nText: """
    answer = client.generate(model =model, prompt = promt_guidance + text + "...\n" + "Option 1: " + option_1 + "\n" + "Option 2: " + option_2 + "\n")
    return answer["response"]


def test_winogrande(number_of_tests_to_run,client, model = 'phi3:mini'):
    winogrande_logger = logging.getLogger("winogrande")
    winogrande_logger.info(f"opening winogrande database\n")
    df = pd.read_json(data_path, lines=True)
    original_prompt_correct_count = 0
    encrypted_prompt_correct_count = 0
    answer_similarity = 0
    embedded_similarity_sum = 0
    percentage_words_replaced_avrage = 0
    for index, row in df.iterrows():
        try:
            print(f"winogrande - {model} - {index}")
            sentence = row['sentence']
            option_1 = row['option1']
            option_2 = row['option2']
            answer = row['answer']
            winogrande_logger.info(
                f"{index},{datetime.datetime.now()},model: {model}, sentence: {sentence},answer: {answer}\n"
            )

            # Get encryption dictionary for prompt and encrypt it and get answers
            prompt_encryption_dict = common.get_encryption_dict(sentence,client, model)
            encrypted_sentence, percentage_words_replaced = common.encrypt_text(sentence,prompt_encryption_dict)
            encrypted_option_1 = common.encrypt_text(option_1,prompt_encryption_dict)[0]
            encrypted_option_2 = common.encrypt_text(option_2,prompt_encryption_dict)[0]
            

            original_prompt_answer = winogrande_get_answer(sentence, option_1,option_2,client, model)
            encrypted_prompt_answer = winogrande_get_answer(encrypted_sentence, encrypted_option_1,encrypted_option_2, client, model)

            original_prompt_extracted_answer = common.extract_answer(original_prompt_answer)
            encrypted_prompt_extracted_answer = common.extract_answer(encrypted_prompt_answer)

            original_prompt_correctness = 1 if common.check_match(str(answer),str(original_prompt_extracted_answer), [option_1,option_2]) else 0
            encrypted_prompt_correctness = 1 if common.check_match(str(answer),str(encrypted_prompt_extracted_answer), [option_1,option_2]) else 0
            original_prompt_correct_count += original_prompt_correctness
            encrypted_prompt_correct_count += encrypted_prompt_correctness
            same_answer = 1 if common.check_match(str(original_prompt_correctness),str(encrypted_prompt_correctness)) else 0
            answer_similarity += same_answer
            embedded_similarity = embedding_eval.cosine_similarity(embedding_eval.get_embedding(encrypted_sentence),embedding_eval.get_embedding(sentence))
            embedded_similarity_sum += embedded_similarity
            percentage_words_replaced_avrage += percentage_words_replaced
            winogrande_logger.info(
    f"""@@@@
    {datetime.datetime.now()}, model: {model}, index: {index}
    sentences: {sentence}
    option1: {option_1}
    option2: {option_2}
    answer: {answer}

    prompt_encryption_dict: {prompt_encryption_dict}

    encrypted_sentence: {encrypted_sentence}
    encrypted_option_1: {encrypted_option_1}
    encrypted_option_2: {encrypted_option_2}
    original_prompt_answer: {original_prompt_answer}
    encrypted_prompt_answer: {encrypted_prompt_answer}
    extracted_original_prompt_answer: {original_prompt_extracted_answer}
    extracted_encrypted_prompt_answer: {encrypted_prompt_extracted_answer}
    (original_prompt_correctness,encrypted_prompt_correctness): ({original_prompt_correctness},{encrypted_prompt_correctness})
    similar_answer: {same_answer}
    Cosine similarity- sentence: {embedded_similarity}
    percentage_words_replaced: {percentage_words_replaced}
    """
            )
        except Exception as e:
            winogrande_logger.error(f"ERROE: {e}\nAT INDEX: {index}\nAT MODEL: {model}\nAT TIME: {datetime.datetime.now()}")
            break
        if index >= number_of_tests_to_run:
            break
    return original_prompt_correct_count , encrypted_prompt_correct_count, answer_similarity, embedded_similarity_sum, percentage_words_replaced_avrage, index+1


if __name__ == '__main__':
    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull("phi3:mini")
    winogrande_logger = common.init_logs(log_path, 'w')
    original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_winogrande(-1,client)
    winogrande_logger.info(f"Finished: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")

def main(number_of_test_to_run,client, models):
    winogrande_logger = logging.getLogger("winogrande")
    winogrande_logger.info(f"Starting winogrande_eval.py\n")
    model_results = {}
    for model in models:
        original_prompt_correct_count , emoji_prompt_correct_count, answer_similarity, avrage_embedding_similarity,percentage_words_replaced_avrage, test_count = test_winogrande(number_of_test_to_run, client, model)
        model_results[model + "_original"] = original_prompt_correct_count/test_count
        model_results[model + "_encrypted"] = emoji_prompt_correct_count/test_count
        model_results[model + "_answer_similarity"] = answer_similarity/test_count
        model_results[model + "_avrage_embedding_similarity"] = avrage_embedding_similarity/test_count
        model_results[model + "percentage_words_replaced_avrage"] = percentage_words_replaced_avrage/test_count
        winogrande_logger.info(
            f"""Finished winogrande with {model} with {test_count} tests:
{model}"_original": {model_results[model + "_original"]}
{model}"_encrypted": {model_results[model + "_encrypted"]}
{model}"_answer_similarity": {model_results[model + "_answer_similarity"]}
{model}"_avrage_embedding_similarity": {model_results[model + "_avrage_embedding_similarity"]}
{model}"percentage_words_replaced_avrage": {model_results[model + "percentage_words_replaced_avrage"]}%
"""
)
        main_logger = logging.getLogger("main")
        main_logger.info(
            f"""Finished winogrande with {model} with {test_count} tests:
{model}"_original": {model_results[model + "_original"]}
{model}"_encrypted": {model_results[model + "_encrypted"]}
{model}"_answer_similarity": {model_results[model + "_answer_similarity"]}
{model}"_avrage_embedding_similarity": {model_results[model + "_avrage_embedding_similarity"]}
{model}"percentage_words_replaced_avrage": {model_results[model + "percentage_words_replaced_avrage"]}%
"""
)
    print(model_results)
    return model_results
