import ollama
import logging
import os
import threading

import drop_eval
import embedding_eval
import hellaswag_eval
import winogrande_eval
import common
import datetime

#add global var of how many tokens were sent to the server

models = ["llama3:8b", "phi3:mini"]

main_log_path = '~/Emoji/Emojicrypt/log/main.log'
wrong_format_log_path = '~/Emoji/Emojicrypt/log/wrong_format_encryption.log'
winogrande_log_path = '~/Emoji/Emojicrypt/log/winogrande_eval.log'
hellaswag_log_path = '~/Emoji/Emojicrypt/log/hellaswag_eval.log'
drop_log_path = '~/Emoji/Emojicrypt/log/drop_eval.log'
embedding_log_path = '~/Emoji/Emojicrypt/log/embedding_eval.log'


main_log_path = os.path.expanduser(main_log_path)
wrong_format_log_path = os.path.expanduser(wrong_format_log_path)
winogrande_log_path = os.path.expanduser(winogrande_log_path)
hellaswag_log_path = os.path.expanduser(hellaswag_log_path)
drop_log_path = os.path.expanduser(drop_log_path)
embedding_log_path = os.path.expanduser(embedding_log_path)

def init_logs():
    main_logger = common.init_logs(main_log_path, 'main')
    encryption_logger = common.init_logs(wrong_format_log_path, 'wrong format encryption')
    winogrande_logger = common.init_logs(winogrande_log_path, 'winogrande')
    hellaswag_logger = common.init_logs(hellaswag_log_path, 'hellaswag')
    drop_logger = common.init_logs(drop_log_path, 'drop')
    embedding_logger = common.init_logs(embedding_log_path, 'embedding')

    main_file_handler = logging.FileHandler(main_log_path)
    encryption_format_file_handler = logging.FileHandler(wrong_format_log_path)
    winogrande_file_handler = logging.FileHandler(winogrande_log_path)
    hellaswag_file_handler = logging.FileHandler(hellaswag_log_path)
    drop_file_handler = logging.FileHandler(drop_log_path)
    embedding_file_handler = logging.FileHandler(embedding_log_path)

    main_logger.addHandler(main_file_handler)
    encryption_logger.addHandler(encryption_format_file_handler)
    winogrande_logger.addHandler(winogrande_file_handler)
    hellaswag_logger.addHandler(hellaswag_file_handler)
    drop_logger.addHandler(drop_file_handler)
    embedding_logger.addHandler(embedding_file_handler)

    main_logger.propagate = False
    encryption_logger.propagate = False
    winogrande_logger.propagate = False
    hellaswag_logger.propagate = False
    drop_logger.propagate = False
    embedding_logger.propagate = False



def run_evaluation(test_func,test_name, number_of_tests_to_run, client, models):
    time_start = datetime.datetime.now()
    test_func(number_of_tests_to_run, client, models)
    time_elapsed = datetime.datetime.now() - time_start
    main_logger.info(f"Finished {test_name}, time: {time_elapsed}\n")
    print(f"Finished {test_name}, time: {time_elapsed}\n")


if __name__ == '__main__':
    
    client = ollama.Client(host='http://172.23.81.3:11434')
    init_logs()
    main_logger = logging.getLogger("main")

    for model in models:
        try:
            print(f"getting {model}")
            main_logger.info(f"Client pulling {model}\n")
            client.pull(model)
            print(f"got {model}")
        except Exception as e:
            print(f"failed to pull {model}")
            main_logger.info(f"Client failed to pull {model}, Exception: {e}\n")

    main_logger.info(f"Finished initializing, starting to run tests\n")

    threads = []
    tests = [
        (drop_eval.main, 'drop_eval.py'), 
        #(embedding_eval.main, 'embedding_eval.py'),
        (hellaswag_eval.main, 'hellaswag_eval.py'), 
        (winogrande_eval.main, 'winogrande_eval.py')
    ]
    
    for test_func, test_name in tests:
        if (test_func == drop_eval.main):
            thread = threading.Thread(target=run_evaluation, args=(test_func,test_name,200,client,models))
        else:
            thread = threading.Thread(target=run_evaluation, args=(test_func,test_name,1000,client,models))
        threads.append(thread)
        thread.start()

    # Waiting for all threads to complete
    for thread in threads:
        thread.join()

    main_logger.info("All evaluations completed.\n")

    # time = datetime.datetime.now()
    # drop_eval.main(1, client, models)
    # main_logger.info(f"Finished drop_eval.py, time: {datetime.datetime.now()-time}\n")
    # time = datetime.datetime.now()
    # hellaswag_eval.main(1, client, models)
    # main_logger.info(f"Finished hellaswag_eval.py, time: {datetime.datetime.now()-time}\n")
    # time = datetime.datetime.now()
    # winogrande_eval.main(1, client, models)
    # main_logger.info(f"Finished hellaswag_eval.py, time: {datetime.datetime.now()-time}\n")
    # #embedding_eval.main(client,models)