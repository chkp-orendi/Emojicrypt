class Obfuscator:
    def __init__(self):
        pass

    def obfuscate(self, user_prompt):
        pass

    def deobfuscate(self, obfuscated_answer):
        pass

    def get_dictionary(self):
        if hasattr(self, "_dictionary_used"):
            return self._dictionary_used
        return {}