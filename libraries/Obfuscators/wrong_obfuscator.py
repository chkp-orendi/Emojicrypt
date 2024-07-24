# Replace the second part of the prompt with a completely irrelevant text
class WrongObfuscator(Obfuscator):
    def __init__(self):
        pass

    def obfuscate(self, user_prompt):
        return user_prompt[0:int(len(user_prompt)/2)] + "... also a quick brown fox jumps over a lazy cpdog"

    def deobfuscate(self, obfuscated_answer):
        return obfuscated_answer
