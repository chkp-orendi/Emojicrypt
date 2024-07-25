import json
import os

from plotly import express as px
import pandas as pd

def plot_metrics_json(metrics):
    df_structure = {
        'obfuscator': [],
        'term_retention': [],
        'prompt_similarity': [],
        'response_similarity': []
    }
    df = pd.DataFrame(df_structure)
    for obfuscator in metrics:
        obfuscator_name = obfuscator[0]
        obfuscator_prompts = obfuscator[1]
        for obfuscator_values in obfuscator_prompts:
            prompt_metrics = obfuscator_values['prompt_metric']
            response_metrics = obfuscator_values['answer_metric']
            df.loc[len(df)] = [obfuscator_name, prompt_metrics['leftovers'], prompt_metrics['similarity'], response_metrics]

    
    # Calculate average and minimum values
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
    
    print(melted_df)

    # Creating the bar chart with 'pseudo' sub-groups
    fig = px.bar(melted_df, x='obfuscator', y='value', 
                 facet_col='statistic', barmode='group',
                 category_orders={"statistic": ["average_value", "minimum_value"], "metric_type": ["Similarity", "Term retention"]})
    
    fig.update_layout(
        title='Metrics by Obfuscator and Metric Type',
        xaxis_title='Obfuscator',
        yaxis_title='Value'
    )
    
    fig.show()


def main():
    data_to_use = "2024-07-24_21_31_28.816609-metrics.json"
    inputfile_path = os.path.join(os.path.dirname(__file__), "metrics", data_to_use)
    with open(inputfile_path, 'r') as file:
        data = json.load(file)
    
    plot_metrics_json(data)

if __name__ == "__main__":
    main()
