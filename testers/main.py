import ollama
import logging
import os

import drop_eval
import embedding_eval
import hellaswag_eval
import winogrande_eval
import common
models = ["llama3:8b", "phi3:mini"]
log_path = '~/Emoji/Emojicrypt/log/main.log'

#cert_path = '~/Emoji/Emojicrypt/ca-certificates.crt'
#os.environ["REQUESTS_CA_BUNDLE"]=cert_path


if __name__ == '__main__':
    

    client = ollama.Client(host='http://172.23.81.3:11434')
    client.pull("phi3:mini")
    logger = common.init_logs(log_path, 'm')
    for model in models:
        try:
            print(f"getting {model}")
            logger.info(f"Client pulling {model}\n")
            client.pull(model)
            print(f"got {model}")
        except Exception as e:
            logger.info(f"Client failed to pull {model}, Exception: {e}\n")

    logger.info(f"Finished initializing, starting to run tests\n")
    #drop_eval.main(3, client, models)
    #hellaswag_eval.main(3, client, models)
    #winogrande_eval.main(3, client, models)
    embedding_eval.main(client,models)


