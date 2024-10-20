import sys
import re
from typing import Dict
import re
import sys
import os


from src.utils.azure_client import get_answer
from src.Obfuscators.phase_1_obfuscator import PhaseOneObfuscator
"""
This is a prototype obfuscator I will pass to the GW to see how it works.
"""

def main(argv: list[str], argc: int):
    if argc ==1:
        print("No arguments provided")
        return
    prompt = argv[1]
    print("prompt: ", prompt)

def write_hello_world_to_file():
    with open('output.txt', 'w') as file:
        file.write("Hello World")

if __name__ == '__main__':
    print("starting\n")
    write_hello_world_to_file()
    # main(sys.argv, len(sys.argv))


