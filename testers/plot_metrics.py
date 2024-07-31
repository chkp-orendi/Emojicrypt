import json
import os

import numpy as np
from plotly import express as px
import pandas as pd
import glob

def plot_statistics(df):
    stats_df = df.groupby(['obfuscator']).agg(
        average_retention=('term_retention', 'mean'),
        top_decile_retention=('term_retention', lambda x: x.quantile(0.9)),
        average_prompt_similarity=('prompt_similarity', 'mean'),
        top_decile_prompt_similarity=('prompt_similarity', lambda x: x.quantile(0.9)),
        average_response_similarity=('response_similarity', 'mean'),
        top_decile_response_similarity=('response_similarity', lambda x: x.quantile(0.9)),
    ).reset_index()

    # Melt the DataFrame to have a long-form DataFrame suitable for Plotly
    melted_df = stats_df.melt(id_vars=['obfuscator'], 
                              value_vars=['average_retention', 'top_decile_retention',
                                          'average_prompt_similarity', 'top_decile_prompt_similarity',
                                          'average_response_similarity', 'top_decile_response_similarity'],
                              var_name='statistic', value_name='value')
    
    # Creating the bar chart with 'pseudo' sub-groups
    fig = px.bar(melted_df, x='statistic', y='value', 
                facet_col='obfuscator', barmode='group',
                color = 'statistic'
                )
    
    fig.update_layout(
        title='Metrics by Obfuscator and Metric Type',
        xaxis_title='Obfuscator',
        yaxis_title='Value',
        bargap=0.1,
        bargroupgap=0.00001
    )
    fig.update_traces(width=0.5)
    # Rename the title of each subplot
    for annotation in fig.layout.annotations:
        if 'obfuscator=' in annotation.text:
            obfuscator_name = annotation.text.split('=')[1]
            annotation.text = f'{obfuscator_name}'


    fig.show()
    return fig

def plot_individual_metrics(df_unfiltered, sample_count, from_first_n):
    np.random.seed(0)
    sample = set(np.random.permutation(from_first_n)[0:sample_count])
    df = df_unfiltered[df_unfiltered['question_index'].isin(sample)]
    df_prompt = df[['obfuscator', 'term_retention', 'prompt_similarity', 'obfuscated_question', 'question_index']].copy()
    df_answer = df[['obfuscator', 'response_similarity', 'deobfuscated_answer', 'question_index']].copy() 

    # Melt the DataFrame to have a long-form DataFrame suitable for Plotly
    melted_df_prompt = df_prompt.melt(id_vars=['obfuscator', 'obfuscated_question', 'question_index'], 
                                      value_vars=['term_retention', 'prompt_similarity'],
                                      var_name='metric_type', value_name='value')
    melted_df_answer = df_answer.melt(id_vars=['obfuscator', 'deobfuscated_answer', 'question_index'], 
                                      value_vars=['response_similarity'],
                                      var_name='metric_type', value_name='value')
    
    melted_df_answer.rename(columns={'deobfuscated_answer': 'llm_text'}, inplace=True)
    melted_df_prompt.rename(columns={'obfuscated_question': 'llm_text'}, inplace=True)

    df_final = pd.concat([melted_df_prompt, melted_df_answer], ignore_index=True)

    fig = px.bar(df_final, x='metric_type', y='value', 
                facet_col='question_index', barmode='group',
                color = 'obfuscator', hover_data={'llm_text': True, 'metric_type': False, 'value': False, 'question_index': False, 'obfuscator': False}
                )
    
    fig.update_layout(
        title='Individual answers',
        xaxis_title='Obfuscator',
        yaxis_title='Value'
    )

    fig.show()
    return fig 

def plot_metrics_json(metrics):
    df_structure = {
        'obfuscator': [],
        'term_retention': [],
        'prompt_similarity': [],
        'response_similarity': [],
        'obfuscated_question': [],
        'deobfuscated_answer': [],
        'question_index': [],
    }
    df = pd.DataFrame(df_structure)
    for obfuscator in metrics:
        qindex = 0
        obfuscator_name = obfuscator[0]
        obfuscator_prompts = obfuscator[1]
        for obfuscator_values in obfuscator_prompts:
            if len(obfuscator_values) <= 1:
                continue
            prompt_metrics = obfuscator_values['prompt_metric']
            response_metrics = obfuscator_values['answer_metric']
            df.loc[len(df)] = [obfuscator_name,
                                 prompt_metrics['leftovers'], prompt_metrics['similarity'],
                                 response_metrics,
                                 obfuscator_values['obfuscated_prompt'],
                                 obfuscator_values['deobfuscated_answer'].replace("\n", "<br>"),
                                 qindex
                              ]
            qindex += 1

    # Calculate average and decile values
    return plot_statistics(df), plot_individual_metrics(df, 4, qindex)
    

def save_folder_plots(data_path):
    json_files = glob.glob(os.path.join(data_path, "*.json"))
    
    for json_file in json_files:
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        fig_statistic, fig_examples = plot_metrics_json(data)
        
        # Save the plot as an image file
        output_file = os.path.splitext(json_file)[0] + "_statistic.html"
        fig_statistic.write_html(output_file)
        output_file = os.path.splitext(json_file)[0] + "_example.html"
        fig_examples.write_html(output_file)

def main():

    data_path = "C:\\Users\\orendi\\Documents\\EmojiCrypt-main\\Emojicrypt\\Presentation"
    data_path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "testers", "metrics", "30-7-Test-Result", "azure_metric")
    
    # data_to_use = "2024-07-30_11_54_18.347697-metrics-llama.json"
    #inputfile_path = os.path.join(os.path.dirname(__file__), "metrics", data_to_use)
    inputfile_path = os.path.join(data_path, "gpt-metric-0.json")
    with open(inputfile_path, 'r') as file:
        data = json.load(file)
    
    plot_metrics_json(data)
        


if __name__ == "__main__":
    main()
