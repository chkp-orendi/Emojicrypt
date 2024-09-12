import pandas as pd
import numpy as np
from plotly import express as px
import matplotlib.pyplot as plt

import os
import sys
import json
import datetime
from typing import List, Callable, Tuple


from dotenv import load_dotenv 
load_dotenv()

## handles json format: [[obfuscator_name, [prompt_dict, prompt_dict, ...]], [obfuscator_name, [prompt_dict, prompt_dict, ...]], ...]

class PlotClass:
    """
    Args:
        inputfile_path (`str`): path to the json file containing the data
        metrics (`list`): list of metrics to be plotted
    """
    def _handle_dict_metric(self, data, metrics):
        for metric in metrics:
            need_handling = False
            if isinstance(data[0][1][0][metric],dict):
                    need_handling = True
                    break 
        if not need_handling:
            return data
        for metric in metrics:
            for obf_index, obfuscator in enumerate(data):
                for test_index, test in enumerate(obfuscator[1]):
                    if isinstance(test[metric],dict):
                        for key in test[metric].keys():
                            data[obf_index][1][test_index][metric + "_"+ key] = data[obf_index][1][test_index][metric][key]
                        data[obf_index][1][test_index].pop(metric)
        return data
    
    def __init__ (self, inputfile_path, metrics):
        with open(inputfile_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        data = self._handle_dict_metric(data,metrics)
        
        df_list = []
        for obfuscator in data:
            df_structure = pd.DataFrame(obfuscator[1])
            if obfuscator[0] == "ContextReletiveObfuscator":
                df_structure['ObfuscatorName'] = "ContextRelativeObfuscator"
            df_structure['ObfuscatorName'] = obfuscator[0]
            df_structure['question_index'] = df_structure.index 

            df_list.append(df_structure)

        self._df = pd.concat(df_list, ignore_index=True)
    
    def generate_statistic_figure(self,prompt_metrics: List[str],answer_metrics: List[str], list_messurements: List[Tuple[str,Callable[[pd.Series], float]]]):
        agg_dict = {}

        for prompt_metric in prompt_metrics:
            for messurement_name, messurement_function in list_messurements:
                agg_dict[f"{messurement_name} {prompt_metric}"] = (prompt_metric, messurement_function)
        for answer_metric in answer_metrics:
            for messurement_name, messurement_function in list_messurements:
                agg_dict[f"{messurement_name} {answer_metric}"] = (answer_metric, messurement_function)

                
        value_vars = list(agg_dict.keys())
        agg_dict = {k:v for k,v in sorted(agg_dict.items(), key=lambda x: x[0])}
        # dict(sorted(agg_dict.items()))
        stats_df = self._df.groupby(['ObfuscatorName']).agg(**agg_dict).reset_index()

        # Melt the DataFrame to have a long-form DataFrame suitable for Plotly
        melted_df = stats_df.melt(id_vars=['ObfuscatorName'], 
                              value_vars=value_vars,
                              var_name='statistic', value_name='value')

        fig = px.bar(melted_df, x='statistic', y='value', 
                facet_col='ObfuscatorName', barmode='group',
                color = 'statistic'
                )
    
        fig.update_layout(
        title='Metrics by Obfuscator and Metric Type',
        xaxis_title='ObfuscatorName',
        yaxis_title='Value',
        bargap=0.1,
        bargroupgap=0.00001
            )
        fig.update_traces(width=0.5)

        # Rename the title of each subplot
    
        for annotation in fig.layout.annotations:
            if 'ObfuscatorName=' in annotation.text:
                obfuscator_name = annotation.text.split('=')[1]
                annotation.text = f'{obfuscator_name}'
    
        # sorted_annotations = sorted(fig.layout.annotations, key=lambda x: int(x.text.split('-')[1]))
        sorted_annotations = fig.layout.annotations
        print(sorted_annotations)
        fig.layout.annotations = sorted_annotations


        # fig.update_layout(xaxis={'categoryorder':'category descending'})
        fig.update_xaxes(categoryorder='array', categoryarray= ['average prompt_metric_llm_score',
                                                                'average answer_metric_llm_similarity',
                                                                'average prompt_metric_precentage_of_changed_word',
                                                                'average prompt_metric_guessed_correct',
                                                                # 'average score for decryption attemp'
                                                                # 'top decile prompt_metric_llm_similarity',
                                                                # 'top decile answer_metric_llm_similarity',
                                                                # 'bottom decile prompt_metric_llm_similarity',
                                                                # 'bottom decile answer_metric_llm_similarity',
                                                                # 'top decile prompt_metric_precentage_of_changed_word',
                                                                # 'top decile answer_metric_precentage_of_changed_word',
                                                                # 'bottom decile prompt_metric_precentage_of_changed_word',
                                                                # 'bottom decile answer_metric_precentage_of_changed_word'
                                                                ])
        return fig
    

    def show_statistic_graph(self,prompt_metric: List[str],answer_metric: List[str], list_messurements: List[Tuple[str,Callable[[pd.Series], float]]]):
        self.generate_statistic_figure(prompt_metric,answer_metric, list_messurements).show()
    def save_statistic_graph(self,prompt_metric,answer_metric, list_messurements, save_path):
        self.generate_statistic_figure(prompt_metric,answer_metric, list_messurements).write_html(save_path + "_statistic_graph.html")

    def generate_individual_figure(self,prompt_metric,answer_metric,sample_size):
        np.random.seed(0)
        data_size = (self._df['ObfuscatorName'] == self._df['ObfuscatorName'].unique().tolist()[0]).sum()
        sample = np.random.choice(data_size, size=sample_size, replace=False)


        df = self._df[self._df['question_index'].isin(sample)]
        df_prompt = df[['ObfuscatorName'] + prompt_metric + ['obfuscated_prompt', 'question_index']].copy()
        df_answer = df[['ObfuscatorName'] + answer_metric + ['deobfuscated_answer', 'question_index']].copy() 
    
        melted_df_prompt = df_prompt.melt(id_vars=['ObfuscatorName', 'obfuscated_prompt', 'question_index'], 
                                            value_vars=prompt_metric,
                                            var_name='metric_type', value_name='value')
        melted_df_answer = df_answer.melt(id_vars=['ObfuscatorName', 'deobfuscated_answer', 'question_index'], 
                                        value_vars=answer_metric,
                                        var_name='metric_type', value_name='value')
        melted_df_answer.rename(columns={'deobfuscated_answer': 'llm_text'}, inplace=True)
        melted_df_prompt.rename(columns={'obfuscated_prompt': 'llm_text'}, inplace=True)

        df_final = pd.concat([melted_df_prompt, melted_df_answer], ignore_index=True)

        fig = px.bar(df_final, x='metric_type', y='value', 
                    facet_col='question_index', barmode='group',
                    color = 'ObfuscatorName', hover_data={'llm_text': True, 'metric_type': False, 'value': False, 'question_index': False, 'ObfuscatorName': False}
                    )
        
        fig.update_layout(
            title='Individual answers',
            xaxis_title='ObfuscatorName',
            yaxis_title='Value'
        )

        
        return fig 
     
    def show_individual_graph(self,prompt_metric,answer_metric, sample_size):
        self.generate_individual_figure(prompt_metric,answer_metric, sample_size).show()
    def save_individual_graph(self,prompt_metric,answer_metric, sample_size, save_path):
        self.generate_individual_figure(prompt_metric,answer_metric, sample_size).write_html(save_path + "_individual_graph.html")

    def save_statistic_scatter_graph(self, metricA: str, metricB: str, save_path: str):
        correlation = self._df[metricA].corr(self._df[metricB])
        px.scatter(self._df, x=metricA, y=metricB, color='ObfuscatorName',
            title=f"Correlation between {metricA} and {metricB}: {correlation}"
            ).write_html(save_path + "scatter_graph.html")

    
    def show_statistic_scatter_graph(self, metricA: str, metricB: str):
        
        correlation_df = self._df.groupby('ObfuscatorName')[[metricA, metricB]].apply(lambda group: group[metricA].corr(group[metricB])).reset_index(level=0, drop=True)
        obfuscators = self._df.groupby('ObfuscatorName')
        correlation_dict = {}
        for name, corr in zip(obfuscators, correlation_df):
            correlation_dict[name] = corr

        self._df['correlation'] = self._df['ObfuscatorName'].map(correlation_dict)
                
        print(correlation_df)
        fig = px.scatter(self._df, x=metricA, y=metricB, color='ObfuscatorName', hover_data=['correlation'])

        fig.show()

        # correlation = self._df[metricA].corr(self._df[metricB])
        # px.scatter(
        #     self._df, x=metricA, y=metricB, color='ObfuscatorName',
        #     title=f"Correlation between {metricA} and {metricB}: {correlation}"
        #     #size='prompt_metric_llm_similarity'
        #     ).show()

if __name__ == "__main__":
    file_name = "Smart random and context checkpoint.json"
    
    inputfile_path = os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024", "2024-09-11", file_name)
    metrics = ["prompt_metric","answer_metric"]
    
    graph = PlotClass(inputfile_path, metrics)


    outputfile_folder = os.path.join(os.getenv("PROJECT_PATH"),"data","September-2024", os.getenv("DATE"))
    os.makedirs(outputfile_folder, exist_ok=True)
    outputfile_path = os.path.join(outputfile_folder, "software development results fixed")

    list_messurements = [
        ("average", 'mean')
        # ("top decile", lambda x: x.quantile(0.9)),
        # ("bottom decile", lambda x: x.quantile(0.1))
    ]

    # graph.show_statistic_graph(["prompt_metric_llm_similarity"],["answer_metric_llm_similarity"],list_messurements)
    # graph.save_statistic_graph(["prompt_metric_llm_similarity", "prompt_metric_precentage_of_changed_word"],["answer_metric_llm_similarity", "answer_metric_precentage_of_changed_word"],list_messurements,outputfile_folder)
    graph.show_statistic_graph(["prompt_metric_llm_score", "prompt_metric_precentage_of_changed_word", "prompt_metric_guessed_correct"],["answer_metric_llm_similarity"],list_messurements)
    # graph.save_statistic_graph([],["answer_metric_unwanted_emoji"],[( "average", 'mean'),("count", lambda x: (x > 0).sum())], outputfile_path)
    # graph.show_statistic_graph([],["answer_metric_unwanted_emoji"],[( "average", 'mean'),("count", lambda x: (x > 0).sum())])