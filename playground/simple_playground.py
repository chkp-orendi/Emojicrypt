from dotenv import load_dotenv 
import os
import sys
import statistics
import numpy as np


load_dotenv()
sys.path.append(os.getenv("PROJECT_PATH"))
from src.utils.azure_client import get_answer
from src.utils.answer_extraction import extract_number


answer_prompt = """Grade the similarity between the following two texts on a scale of 0.0 to 1.0 with emphasis on technical terms changed with relative emojis. A score of 0.0 means the emojis are not relevant or there were technical words to change and it didn't. A score of 1.0 means all the technical terms were changed with relative emojis.
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>
"""

query_prompt = """give a number between 0.0 to 1.0 where 0.0 is not similar at all and 1.0 is the exact same text for the similarity for these 2 texts:
Text1: {text1}
Text2: {text2}
Please provide the similarity score along with a brief explanation of the rationale behind the score. Print $ANSWER: <number>"""



def evaluate_prompt(obfuscated_prompt, case_data):
    query = query_prompt.format(text1=obfuscated_prompt, text2=case_data) 
    answer = get_answer(query)
    print(answer)
    print("EXTRACTED NUMBER: ", extract_number(answer))
    print("___________________________________________________________________________________________________________________________")
    return extract_number(answer)

def evaluate_answer( obfuscated_prompt, case_data):
    query = answer_prompt.format(text1=obfuscated_prompt, text2=case_data) 
    answer = get_answer(query)
    print(answer)
    print("EXTRACTED NUMBER: ", extract_number(answer))
    print("___________________________________________________________________________________________________________________________")
    return extract_number(answer)



import json
text1= "\"How does the use of machine learning algorithms in predictive analytics enhance decision-making processes in businesses, and what are some common challenges faced during implementation?"
text2 = "\"How does the use of 🍀🚀🎨 in 🎉✨🌍 enhance 🌟🍀 in 🌍📚, and what are some common challenges faced during implementation?" 
#text2 = "How does the use of 🤖📊 in 🔮📈 enhance 🧠📊 in businesses, and what are some common challenges faced during 🚀?"


# print("text2: ", text2_json)
# text2= "\"How does the use of \ud83e\udd16\ud83d\udcda\ud83d\udd04 in \ud83d\udd2e\ud83d\udcca\ud83d\udcc8 enhance \ud83e\udde0\ud83d\uddf3\ufe0f\ud83d\udd04 in \ud83c\udfe2\ud83d\udcbc, and what are some common challenges faced during implementation?"
# text3 = "The use of machine learning algorithms in predictive analytics enhances decision-making processes in businesses by improving efficiency, accuracy, and decision-making processes. However, common challenges during implementation include data quality issues, integration complexities, and resistance to change from employees"
# text4 = "Machine learning algorithms in predictive analytics can significantly enhance decision-making processes in businesses in several ways:\n\n1. Improved Accuracy: Machine learning algorithms can analyze vast amounts of data and identify patterns and trends that humans might miss, leading to more accurate predictions.\n\n2. Efficiency: These algorithms can process data much faster than humans, enabling businesses to make quick decisions.\n\n3. Personalization: Machine learning can help businesses understand their customers better and provide personalized services or products, thereby improving customer satisfaction and loyalty.\n\n4. Risk Management: Predictive analytics can help businesses identify potential risks and take preventive measures.\n\n5. Cost Reduction: By automating data analysis, businesses can reduce the costs associated with manual data analysis.\n\nDespite these benefits, businesses often face several challenges during the implementation of machine learning algorithms in predictive analytics:\n\n1. Data Quality: The accuracy of predictions depends on the quality of data. If the data is incomplete, outdated, or biased, the predictions will be inaccurate.\n\n2. Lack of Expertise: Implementing machine learning algorithms requires a high level of expertise in data science and machine learning, which many businesses lack.\n\n3. Integration: Integrating machine learning algorithms with existing systems can be complex and time-consuming.\n\n4. Privacy and Security: Businesses need to ensure that they comply with data privacy regulations and protect the data from breaches.\n\n5. Interpretability: Machine learning models, especially complex ones like deep learning, can be difficult to interpret. This lack of transparency can make it hard for businesses to trust the predictions"


print(evaluate_prompt(text1, text2))

# # text1 = "a kid walked in the park"
# # text2 = "a kid walked in the park"

# arr_prompt = []
# # arr_answer = []
# for i in range(5):
#     arr_prompt.append(evaluate_prompt(text1, text2))
# #     arr_answer.append(evaluate_answer(text3, text4))


# #arr =  [70, 20, 20, 70, 70, 70, 85, 20, 85, 20]
# print("________________________________________________________________________________________________________________________________________________________________________________________________________________________")
# average = statistics.mean(arr_prompt)
# variance = statistics.pstdev(arr_prompt)
# top_decile = np.percentile(arr_prompt, 90)
# bottom_decile = np.percentile(arr_prompt, 10)
# print("arr_prompt")
# print("Similarity values: ", arr_prompt)
# print("Avrage: ", average)
# print("Variance Root: ", variance)
# print("Top Decile: ", top_decile)
# print("Bottom Decile: ", bottom_decile)
# # print("________________________________________________________________________________________________________________________________________________________________________________________________________________________")
# average = statistics.mean(arr_answer)
# variance = statistics.pstdev(arr_answer)
# top_decile = np.percentile(arr_answer, 90)
# bottom_decile = np.percentile(arr_answer, 10)
# print("arr_answer")
# print("Similarity values: ", arr_answer)
# print("Avrage: ", average)
# print("Variance Root: ", variance)
# print("Top Decile: ", top_decile)
# print("Bottom Decile: ", bottom_decile)