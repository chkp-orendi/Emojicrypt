import ollama
import sys
import os

# Add the directory containing module_to_import.py to the Python path
script_dir = os.path.dirname(__file__)  
parent_dir = os.path.dirname(script_dir)  
target_dir = os.path.join(parent_dir, 'libraries') 
sys.path.append(target_dir)

import AzureApi
import EncryptionAndDecryption
import my_logging

compare_answer_embedding_log_path = '~/Emoji/Emojicrypt/log/compare_answer_embedding_log.log'
data_path = '/root/Emoji/Emojicrypt/data/generated_data/chatgpt_5_questions.txt'

if __name__ == '__main__':
    
    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull("llama3:8b")
    print("got model")
    

    embedding_eval_avrage = 0
    avrage_precentage_words_replaced = 0
    i = 0
    j=0
    logger = my_logging.init_logs(compare_answer_embedding_log_path, 'testing')
    with open(data_path, 'r') as file:
    # Read the file line by line
        for line in file:
            if "Context" in line:
                Last_context = line[10:]
                logger.info(f"Context: {Last_context}\n")
                enc_dict = EncryptionAndDecryption.get_encryption_dict(Last_context, client) 
                logger.info(f"encryption_dict: {enc_dict}\n")
            if "Question" in line:
                Last_question = line[10:]
                formated_question = Last_context+'\n' + Last_question

                original_answer = AzureApi.get_answer(formated_question, "gpt-4")
                encrypted_text, precentage_words_replaced = EncryptionAndDecryption.get_encryption_text(formated_question, enc_dict)
                logger.info(f"precentage_words_replaced: {precentage_words_replaced}\n")

                logger.info(f"encrypted_text: {encrypted_text}\n")
                logger.info(f"original_answer: {original_answer}\n")
                encrypted_answer = AzureApi.get_answer(encrypted_text, "gpt-4")
                logger.info(f"encrypted_answer: {encrypted_answer}\n")
                decrypted_answer = EncryptionAndDecryption.get_decryption_text(encrypted_answer, enc_dict)
                logger.info(f"decrypted_answer: {decrypted_answer}\n")

                embedding_similarity = AzureApi.cosine_similarity(original_answer, decrypted_answer)
                logger.info(f"embedding_similarity: {embedding_similarity}\n")
                embedding_eval_avrage += embedding_similarity
                avrage_precentage_words_replaced +=precentage_words_replaced
                j += 1
                if (j >= 5):
                    break
                

    logger.info(f"embedding_eval_avrage:  {embedding_eval_avrage/j}\n avrage_precentage_words_replaced: {avrage_precentage_words_replaced/j}")
    print(f"embedding_eval_avrage:  {embedding_eval_avrage/j}\n avrage_precentage_words_replaced: {avrage_precentage_words_replaced/j}")
