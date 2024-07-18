import logging
import os

#path should include name, meaning log_path = ".../folder/name.log"
def init_logs(log_path,name):
    # Expand the tilde to the full home directory path
    log_file_path = os.path.expanduser(log_path)

    # Ensure the directory exists
    #os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    logger = logging.getLogger(name)
    return logger
