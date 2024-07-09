import ollama
import embedding_eval
import common
import AzureApi


compare_answer_embedding_log_path = '~/Emoji/Emojicrypt/log/compare_answer_embedding_log.log'

if __name__ == '__main__':
    
    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull("llama3:8b")
    text = "The Python programming language, created by Guido van Rossum and first released in 1991, is a high-level, interpreted programming language that emphasizes code readability. Python's design philosophy prioritizes the use of white space and less cluttered syntax, making it easier for programmers to write clear, logical code for small and large-scale projects. Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. Python interpreters are available for many operating systems, allowing Python code execution on a wide variety of systems."
    print("got model")
    
    data_path = '/root/Emoji/Emojicrypt/data/generated_data/chatgpt_5_questions.txt'

    embedding_eval_avrage = 0
    i = 0
    logger = common.init_logs(compare_answer_embedding_log_path, 'main')
    with open(data_path, 'r') as file:
    # Read the file line by line
        for line in file:
            if "Context" in line:
                Last_context = line[10:]
                logger.info(f"Context: {Last_context}\n")
                enc_dict = common.get_encryption_dict(Last_context, client) 
                logger.info(f"encryption_dict: {enc_dict}\n")
                encrypted_text = common.encrypt_text(Last_context, enc_dict)[0]
                logger.info(f"encrypted_text: {encrypted_text}\n")
            if "Question" in line:
                original_answer = AzureApi.get_answer(Last_context, "gpt-4")
                logger.info(f"original_answer: {original_answer}\n")
                encrypted_answer = AzureApi.get_answer(encrypted_text, "gpt-4")
                logger.info(f"encrypted_answer: {encrypted_answer}\n")
                decrypted_answer = common.decrypt_text(encrypted_answer, enc_dict)
                logger.info(f"decrypted_answer: {decrypted_answer}\n")

                embedding_similarity = embedding_eval.compare_text_embedding_similarity(original_answer, decrypted_answer)
                logger.info(f"embedding_similarity: {embedding_similarity}\n")
                embedding_eval_avrage += embedding_similarity
                break
            i += 1
            


    print(f"embedding_eval_avrage:  {embedding_eval_avrage/i}")