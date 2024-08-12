from typing import Self, Dict, Any

class Obfuscator:
    def __init__(self, name: str) -> Self:
        self._name = name

    def obfuscate(self, user_prompt: Dict[Any,Any]) -> str:
        pass

    # Might change obfuscated_answer to not be str in the future
    def deobfuscate(self, obfuscated_answer: str) -> str:
        pass

    def get_dictionary(self) -> Dict[Any, Any]:
        if hasattr(self, "_dictionary_used"):
            return self._dictionary_used
        return {}
    
    def get_name(self) -> str:
        return self._name