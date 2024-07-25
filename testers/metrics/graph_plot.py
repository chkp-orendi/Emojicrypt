import json
import numpy as np
import plotly.graph_objects as go
import os

import json
import numpy as np
import matplotlib.pyplot as plt




def plotly_graph(data):

    evaluations = ["question similarity avrage","question similarity median" , "answer similarity avrage", "answer similarity median", "question leftovers"]
    # Initialize lists to store averages and medians
    question_averages = 0
    question_medians = []
    left_over_avrage = 0
    answer_averages = 0
    answer_medians = []
    test_size = len(data)

    test_results = {}

    for entry in data:
        name = entry[0]
        for item in entry[1]:

            question_similarity = item["prompt_metric"]["similarity"]  
            list_left_overs = item["prompt_metric"]["leftovers"]  
            answer_similarity = item["answer_metric"]

            question_averages += question_similarity
            question_medians.append(question_similarity)
            left_over_avrage += list_left_overs
            answer_averages += answer_similarity
            answer_medians.append(answer_similarity)


        question_averages = question_averages/test_size
        answer_averages = answer_averages/test_size
        question_median = np.median(question_medians)
        answer_median = np.median(answer_medians)
        left_over_avrage = left_over_avrage/test_size
        test_results[name] = {"question_avg": question_averages, "question_median": question_median, "answer_avg": answer_averages, "answer_median": answer_median, "left_over_avg": left_over_avrage}

    # Create a bar graph with Plotly
    fig = go.Figure(data=[
        go.Bar(name='Average', x=list(range(len(averages))), y=averages),
        go.Bar(name='Median', x=list(range(len(medians))), y=medians)
    ])

    # Update the layout
    fig.update_layout(barmode='group', title='Averages and Medians of Numbers',
                    xaxis_title='Entry Index', yaxis_title='Value')

    # Show the figure
    fig.show()

def matplotlib_graph(data):

    # Initialize a dictionary to hold the metrics for each obfuscator
    metrics = {}

    # Step 3: Calculate Metrics
    for entry in data:
        obfuscator = entry['Obfuscator']
        if obfuscator not in metrics:
            metrics[obfuscator] = {'similarity': [], 'leftovers': [], 'answer_metric': []}
        
        metrics[obfuscator]['similarity'].append(entry['similarity'])
        metrics[obfuscator]['leftovers'].append(entry['leftovers'])
        metrics[obfuscator]['answer_metric'].append(entry['answer_metric'])

    # Calculate average and median for each metric of each obfuscator
    results = {}
    for obfuscator, values in metrics.items():
        results[obfuscator] = {
            'similarity_avg': np.mean(values['similarity']),
            'similarity_median': np.median(values['similarity']),
            'leftovers_avg': np.mean(values['leftovers']),
            'leftovers_median': np.median(values['leftovers']),
            'answer_metric_avg': np.mean(values['answer_metric']),
            'answer_metric_median': np.median(values['answer_metric']),
        }

    # Step 5: Plot the Data
    obfuscators = list(results.keys())
    metrics = ['similarity_avg', 'similarity_median', 'leftovers_avg', 'leftovers_median', 'answer_metric_avg', 'answer_metric_median']

    # Setting up the figure and axes for the bar graph
    fig, ax = plt.subplots(figsize=(10, 8))

    # Number of metrics
    n_metrics = len(metrics)
    # The x locations for the groups
    ind = np.arange(len(obfuscators))  
    # The width of the bars
    width = 0.1  

    for i, metric in enumerate(metrics):
        ax.bar(ind + i*width, [results[obf][metric] for obf in obfuscators], width, label=metric)

    ax.set_xlabel('Obfuscator')
    ax.set_ylabel('Scores')
    ax.set_title('Scores by Obfuscator and Metric')
    ax.set_xticks(ind + width / n_metrics)
    ax.set_xticklabels(obfuscators)
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    # file_path = os.path.join("C:\\Users","orendi","Documents","EmojiCrypt-main","Emojicrypt","testers","metrics","2024-07-23_19_54_22.206368-metrics_star.json")
    # with open(file_path, 'r') as file:
    #     data = json.load(file)

    file_path = os.path.join("C:\\Users","orendi","Documents","EmojiCrypt-main","Emojicrypt","testers","metrics","2024-07-24_18_37_35.805779-metrics.json")
    with open(file_path, 'r') as file:
        data = json.load(file)

    plotly_graph(data)
    #matplotlib_graph(data)