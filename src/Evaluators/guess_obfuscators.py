"""
Given: original answer, obfuscated prompt, an obfuscated answer
guess the emoji sequences in the obfuscated prompt 
"""
from dotenv import load_dotenv 
import sys
import os
load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))

from src.utils.azure_client import get_json_with_histroy
from src.utils.string_utils import contains_emoji

def guess_obfuscators(dictionary_used: dict[str,str], obfuscated_prompt: str, obfuscated_answer: str) -> tuple:
    """
    Returns:
    - 'answer': str: the answer given by the llm
    - 'guessed_correct': int: the number of correct guesses
    - 'number_of_emoji_in_prompt': int: number of emojis in the prompt
    - 'correct_guesses_list': list[tuple]: list of correct guesses
    """
    
    history = [
        {
            "role": "system",
            "content": "You are a translator from emoji sequences to text."
        },
        {
            "role": "user",
            "content": f"""Given the following Text1, Text2. give a list of words you think the emoji sequences in Text1 represent.
Text1: {obfuscated_prompt}
Text2: {obfuscated_answer}
Return json with key are the emojis and value the guessed words"""
        }
    ]
    answer: str = get_json_with_histroy(history)
    dictionary_used = {v:k.lower() for k, v in dictionary_used.items()}
    correct_count = 0
    correct_guesses_list = []
    for line in answer.split('\n')[1:-1]:
        try:
            key, value = line.split(':')
            key = key.strip(' ",\\ \t \n').lower()
            value = value.strip(' ",\\ \t \n').lower()
            if key in dictionary_used.keys():
                if dictionary_used[key] in value or value in dictionary_used[key]:
                    correct_guesses_list.append((key,value))
                    correct_count += 1
        except Exception as e:
            print("error")
            print(e, line)

    number_of_emojis = 0
    for word in obfuscated_prompt.split():
        if contains_emoji(word):
            number_of_emojis += 1
    return answer, correct_count, number_of_emojis, correct_guesses_list

# dictonary = {
#                     "Japanese cinema": "🎮🐦🎲",
#                     "global filmmaking": "🐗🎷",
#                     "Akira Kurosawa": "🎃🦐🦇",
#                     "Yasujirō Ozu": "🎧🎶🦀",
#                     "Hayao Miyazaki": "🎨🐋🐻",
#                     "samurai epics": "🦅🐱",
#                     "Western genres": "🎸\n"
#                 }

# obfuscated_prompt = "🎮🐦🎲 has exerted a profound influence on 🐗🎷, particularly through the works of pioneering directors such as 🎃🦐🦇, 🎧🎶🦀, and 🎨🐋🐻. kurosawa's 🦅🐱 like \"seven samurai\" have inspired 🎸\n, notably influencing john sturges' \"the magnificent seven.\" ozu's meticulous attention to family dynamics and human relationships has shaped narrative techniques in european art cinema. additionally, miyazaki's enchanting animated features from studio ghibli, like \"spirited away,\" have not only redefined animation standards but also profoundly impacted the storytelling landscape of animated films worldwide. 🎮🐦🎲's thematic depth, innovative storytelling, and unique aesthetic sensibilities have left an indelible mark on filmmakers and audiences across the globe.\n\nhow have directors such as 🎃🦐🦇, 🎧🎶🦀, and 🎨🐋🐻 contributed to the global influence of 🎮🐦🎲 through their distinctive works?"
# obfuscated_answer = "Directors such as Akira Kurosawa (🎃🦐🦇), Yasujirō Ozu (🎧🎶🦀), and Hayao Miyazaki (🎨🐋🐻) have significantly contributed to the global influence of Japanese cinema (🎮🐦🎲) through their distinctive works, each bringing unique elements that have resonated with filmmakers and audiences worldwide.\n\n### Akira Kurosawa (🎃🦐🦇)\nKurosawa's films are renowned for their epic storytelling, complex characters, and innovative techniques. His work has had a profound impact on global cinema, particularly in the following ways:\n\n- **Narrative Structure and Themes**: Kurosawa's \"Seven Samurai\" (🦅🐱) is a prime example of his ability to blend action with deep humanism. This film inspired John Sturges' \"The Magnificent Seven,\" showcasing how Kurosawa's storytelling transcended cultural boundaries.\n- **Cinematic Techniques**: Kurosawa's use of dynamic camera movements, weather elements to enhance mood, and the \"wipe\" transition have been widely adopted by filmmakers around the world.\n- **Character Archetypes**: His exploration of moral ambiguity and complex characters has influenced directors like George Lucas and Sergio Leone, who have cited Kurosawa as a major influence on their work.\n\n### Yasujirō Ozu (🎧🎶🦀)\nOzu's films are celebrated for their subtlety, emotional depth, and focus on family and societal changes. His contributions include:\n\n- **Visual Style**: Ozu's use of low camera angles, static shots, and meticulous composition creates a unique visual language that emphasizes the everyday lives of his characters. This style has influenced European art cinema and directors like Wim Wenders.\n- **Narrative Focus**: Ozu's attention to family dynamics and human relationships offers a profound exploration of universal themes, making his films relatable across different cultures.\n- **Pacing and Rhythm**: His deliberate pacing and contemplative storytelling have inspired filmmakers to adopt a more reflective approach to cinema, valuing the quiet moments and the subtleties of human interaction.\n\n### Hayao Miyazaki (🎨🐋🐻)\nMiyazaki's work with Studio Ghibli has redefined animation and storytelling, contributing to the global influence of Japanese cinema through:\n\n- **Innovative Animation**: Films like \"Spirited Away\" have set new standards for animation quality and creativity, influencing animators and studios worldwide.\n- **Thematic Depth**: Miyazaki's films often explore complex themes such as environmentalism, pacifism, and the transition from childhood to adulthood, resonating with audiences of all ages.\n- **Cultural Fusion**: His ability to blend Japanese folklore with universal themes has made his stories accessible and beloved globally, bridging cultural gaps and expanding the reach of Japanese animation.\n\n### Overall Impact\nThe collective works of Kurosawa, Ozu, and Miyazaki have not only showcased the richness of Japanese cinema but also pushed the boundaries of storytelling, visual aesthetics, and thematic exploration. Their influence is evident in various aspects of global cinema, from narrative techniques and character development to visual style and thematic depth. Through their distinctive works, these directors have left an indelible mark on the world of filmmaking, inspiring countless directors and captivating audiences across the globe."


# print(guess_obfuscators(dictonary,obfuscated_prompt,obfuscated_answer ))