class FakeObfuscator:
    def __init__(self):
        pass


    def obfuscate(self, user_prompt):
        return user_prompt

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer
