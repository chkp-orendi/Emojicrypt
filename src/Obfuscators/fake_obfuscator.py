import sys
import os
from typing import Self
from dotenv import load_dotenv 
from logging import Logger, getLogger
from src.Obfuscators.obfuscator_template import Obfuscator
from typing import Dict, List, Union

load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.Obfuscators.obfuscator_template import Obfuscator


def make_fake_obfuscator(args: Dict):
    return lambda: FakeObfuscator(name = args["name"])

class FakeObfuscator(Obfuscator):
    def __init__(self,name: str = "FakeObfuscator") -> Self:
        self._logger = getLogger("__main__")
        super().__init__(name)


    def obfuscate(self, user_prompt: Dict[str, Union[str, List[str]]]) -> str:
        return user_prompt["original_prompt"]

    def deobfuscate(self, obfuscated_answer: str) -> str:
        return obfuscated_answer
