import ollama
import common
import logging
import pandas as pd
import logging
import datetime
import embedding_eval

import os

cert_path = '~/Emoji/Emojicrypt/ca-certificates.crt'
#os.environ["REQUESTS_CA_BUNDLE"]=cert_path
#os.environ["REQUESTS_CA_BUNDLE"]= os.path.expanduser(cert_path)

log_path = '~/Emoji/Emojicrypt/log/hellaswag_eval.log'
data_path = '~/Emoji/Emojicrypt/data/hellaswag-master/data/hellaswag_train.jsonl'


def hellaswag_get_answer(text, endings, client, model = 'llama3:8b'):
    promt_guidance = f"""I will give you 4 options to choose an ending to the following text, pick the most likely one. Think step by step, then write a line of the form "Answer: $ANSWER_NUMBER" at the end of your response. the text:\n"""
    answer = client.generate(model =model, prompt = promt_guidance + text + "...\n" + "Option 0: " + endings[0] + "\n" + "Option 1: " + endings[1] + "\n" + "Option 2: " + endings[2] + "\n" + "Option 3: " + endings[3])
    return answer["response"]

def test_hellaswag(number_of_tests_to_run, client, model = 'phi3:mini'):
    hellaswag_logger = logging.getLogger("hellaswag")
    hellaswag_logger.info(f"opening hellaswag\n")
    df = pd.read_json(data_path ,lines=True ,engine='pyarrow')
    original_prompt_correct_count = 0
    encrypted_prompt_correct_count = 0
    answer_similarity = 0
    embedded_similarity_sum = 0
    percentage_words_replaced_avrage = 0
    for index, row in df.iterrows():
        try:
            print(f"hellaswag - {model} - {index}")
            sentence = row['ctx']
            endings = row['endings']
            answer = row['label']
            hellaswag_logger.info(
    f"{index},{datetime.datetime.now()},model: {model}\n"
            )
            # Get encryption dictionary for prompt and encrypt it and get answers
            prompt_encryption_dict = common.get_encryption_dict(sentence,client, model)
            encrypted_sentence, percentage_words_replaced= common.encrypt_text(sentence,prompt_encryption_dict)
            encrypted_endings = [common.encrypt_text(ending,prompt_encryption_dict)[0] for ending in endings]

            original_prompt_answer = hellaswag_get_answer(sentence, endings,client, model)
            encrypted_prompt_answer = hellaswag_get_answer(encrypted_sentence, encrypted_endings,client, model)

            original_prompt_extracted_answer = common.extract_answer(original_prompt_answer)
            encrypted_prompt_extracted_answer = common.extract_answer(encrypted_prompt_answer)

            original_prompt_correctness = 1 if common.check_match(str(answer),str(original_prompt_extracted_answer),endings) else 0
            encrypted_prompt_correctness = 1 if common.check_match(str(answer),str(encrypted_prompt_extracted_answer),endings) else 0
            original_prompt_correct_count += original_prompt_correctness
            encrypted_prompt_correct_count += encrypted_prompt_correctness
            same_answer = 1 if common.check_match(str(encrypted_prompt_extracted_answer),str(original_prompt_extracted_answer)) else 0
            answer_similarity += same_answer
            embedded_similarity = embedding_eval.cosine_similarity(embedding_eval.get_embedding(encrypted_sentence),embedding_eval.get_embedding(sentence))
            embedded_similarity_sum += embedded_similarity
            percentage_words_replaced_avrage += percentage_words_replaced

            hellaswag_logger.info(
    f"""@@@@
    {datetime.datetime.now()}, model: {model}, index: {index}
    sentences: {sentence}
    endings: {endings}
    answer: {answer}

    prompt_encryption_dict: {prompt_encryption_dict}

    encrypted_sentence: {encrypted_sentence}
    encrypted_endings: {encrypted_endings}
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
            hellaswag_logger.error(f"ERROE: {e}\nAT INDEX: {index}\nAT MODEL: {model}\nAT TIME: {datetime.datetime.now()}")
            break
        if index >= number_of_tests_to_run:
            break

    return original_prompt_correct_count , encrypted_prompt_correct_count, answer_similarity, embedded_similarity_sum,percentage_words_replaced_avrage, index+1

if __name__ == '__main__':
    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull('phi3:mini')
    hellaswag_logger = common.init_logs(log_path, 'h')
    original_prompt_correct_count , emoji_prompt_correct_count, test_count = test_hellaswag(3,client)
    hellaswag_logger.info(f"Finished: original_prompt_correct_count: {original_prompt_correct_count} , emoji_prompt_correct_count:{emoji_prompt_correct_count}, test_count:{test_count}")

def main(number_of_test_to_run,client, models):
    hellaswag_logger = logging.getLogger("hellaswag")
    
    hellaswag_logger.info(f"Starting hellaswag_eval.py\n")
    model_results = {}
    for model in models:
        original_prompt_correct_count , emoji_prompt_correct_count, answer_similarity, avrage_embedding_similarity,percentage_words_replaced_avrage, test_count = test_hellaswag(number_of_test_to_run,client ,model)
        model_results[model + "_original"] = original_prompt_correct_count/test_count
        model_results[model + "_encrypted"] = emoji_prompt_correct_count/test_count
        model_results[model + "_answer_similarity"] = answer_similarity/test_count
        model_results[model + "_avrage_embedding_similarity"] = avrage_embedding_similarity/test_count
        model_results[model + "percentage_words_replaced_avrage"] = percentage_words_replaced_avrage/test_count
        hellaswag_logger.info(
            f"""Finished hellaswag with {model} with {test_count} tests:
{model}"_original": {model_results[model + "_original"]}
{model}"_encrypted": {model_results[model + "_encrypted"]}
{model}"_answer_similarity": {model_results[model + "_answer_similarity"]}
{model}"_avrage_embedding_similarity": {model_results[model + "_avrage_embedding_similarity"]}
{model}"percentage_words_replaced_avrage": {model_results[model + "percentage_words_replaced_avrage"]}%
"""
)
        main_logger = logging.getLogger("main")
        main_logger.info(
            f"""Finished hellaswag with {model} with {test_count} tests:
{model}"_original": {model_results[model + "_original"]}
{model}"_encrypted": {model_results[model + "_encrypted"]}
{model}"_answer_similarity": {model_results[model + "_answer_similarity"]}
{model}"_avrage_embedding_similarity": {model_results[model + "_avrage_embedding_similarity"]}
{model}"percentage_words_replaced_avrage": {model_results[model + "percentage_words_replaced_avrage"]}%
"""
)
    print(model_results)
    return model_results
