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


client = EncryptionAndDecryption.init_Ollama_client()

Context = "The board of directors at Acme Corp has recently expanded from 8 to 12 members to increase diversity"
text = """context:The board of directors at Acme Corp has recently expanded from 8 to 12 members to increase diversity
question:How many new members were added to the board of Acme Corp?
"""


client.pull("llama3:8b")

original_answer = AzureApi.get_answer(text, "gpt-4")
enc_dict = EncryptionAndDecryption.get_encryption_dict(text, client)
encrypted_text, precentage_words_replaced = EncryptionAndDecryption.get_encryption_text(text, enc_dict)
encrypted_answer = AzureApi.get_answer(encrypted_text, "gpt-4")
decrypted_answer = EncryptionAndDecryption.get_decryption_text(encrypted_answer, enc_dict)

print(f"""
$original_answer
{original_answer}
$decrypted_answer
{decrypted_answer}
$enc_dict
{enc_dict}
$encrypted_text
{encrypted_text}
$encrypted_answer
{encrypted_answer}
""")
