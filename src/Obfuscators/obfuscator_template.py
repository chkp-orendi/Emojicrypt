from typing import Self, Dict, Any

class Obfuscator:
    def __init__(self, name: str) -> Self:
        self._name = name

    def obfuscate(self, user_prompt: Dict[Any,Any]) -> str:
        pass

    def deobfuscate(self, obfuscated_answer: str) -> str:
        pass

    def get_dictionary(self) -> Dict[Any, Any]:
        if hasattr(self, "_dictionary_used"):
            return self._dictionary_used
        return {}
    
    def get_terms_list(self) -> Dict[Any, Any]:
        if hasattr(self, "_term_list"):
            return self._term_list
        return []

    def get_dict_reasoning(self) -> str:
        if hasattr(self, "_dict_reasoning"):
            return self._dict_reasoning
        return 
    
    def get_list_reasoning(self) -> str:
        if hasattr(self, "_list_reasoning"):
            return self._list_reasoning
        return 
    
    def get_list_and_dictionary_difference(self) -> int:
        if hasattr(self, "self._term_list") and hasattr(self, "self._dictionary_used"):
            return len(self.self._term_list)-len(self._dictionary_used.keys())
        return 0

    def get_name(self) -> str:
        return self._name