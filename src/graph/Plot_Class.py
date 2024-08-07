import pandas as pd
import numpy as np
from plotly import express as px
import os
import sys
import json
import datetime

from dotenv import load_dotenv 
load_dotenv()

## handles json format: [[obfuscator_name, [prompt_dict, prompt_dict, ...]], [obfuscator_name, [prompt_dict, prompt_dict, ...]], ...]

class Plot:
    
    def _handle_dict_metric(self,data,metric):
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
        with open(inputfile_path, 'r') as file:
            data = json.load(file)
        data = self._handle_dict_metric(data,metrics)
        
        df_list = []
        for obfuscator in data:
            df_structure = pd.DataFrame(obfuscator[1])
            df_structure['ObfuscatorName'] = obfuscator[0]
            df_structure['question_index'] = df_structure.index 

            df_list.append(df_structure)

        self._df = pd.concat(df_list, ignore_index=True)
    
    #input a list of prompt_metric and answer_metric
    def generate_statistic_figure(self,prompt_metric,answer_metric):
        agg_dict = {}
        for metric in prompt_metric:
            agg_dict[f"average {metric}"] = (metric, 'mean')
            agg_dict[f"top decile {metric}"] =  (metric, lambda x: x.quantile(0.9))
            agg_dict[f"bottom decile {metric}"] =  (metric, lambda x: x.quantile(0.1))
        for metric in answer_metric:
            agg_dict[f"average {metric}"] = (metric, 'mean')
            agg_dict[f"top decile {metric}"] =  (metric, lambda x: x.quantile(0.9))
            agg_dict[f"bottom decile {metric}"] =  (metric, lambda x: x.quantile(0.1))

        value_vars = list(agg_dict.keys())
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
    
        return fig
    

    def show_statistic_graph(self,prompt_metric,answer_metric):
        self.generate_statistic_figure(prompt_metric,answer_metric).show()
    def save_statistic_graph(self,prompt_metric,answer_metric,save_path):
        self.generate_statistic_figure(prompt_metric,answer_metric).write_html(save_path + "_statistic_graph.html")

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

if __name__ == "__main__":
    file_name = "RESULTS_2024-08-07_10_46_47.771852gpt_metric_new_test.json"
    
    inputfile_path = os.path.join(os.getenv("PROJECT_PATH"),"data", file_name)
    metrics = ["prompt_metric","answer_metric"]
    
    graph = Plot(inputfile_path, metrics)

    outputfile_path = os.path.join(os.getenv("PROJECT_PATH"),"data","7-8-2024", file_name.strip(".json"))
    graph.save_individual_graph(["prompt_metric"],["answer_metric"],5,outputfile_path)
    graph.save_statistic_graph(["prompt_metric"],["answer_metric"],outputfile_path)
    # for filename in os.listdir(inputfile_path):
    #     if not filename.endswith(".json"):
    #         continue
    #     full_path = os.path.join(inputfile_path,filename)
    #     graph = Plot(full_path, metrics)
    #     graph.save_statistic_graph(["prompt_metric_similarity"],["answer_metric"], full_path)

