import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../libraries'))
import AzureApi
import AnswerExtraction


#This script will handle json with $SCENARIO and $LIST [ex1,ex2,...], and remove the prefix and convert string to list and then will add embedding and answer.

def extract_scenario(data):
    return data["scenario"][11:-1] # remove $SCENARIO. Will need to for every new generation.

def extract_list(data):
    print(data["list"])
    return AnswerExtraction.extract_list(data["list"])

def add_original_embeddings(data):
    return AzureApi.get_embedding(data["scenario"], model="text-embedding-3-small")

def add_answer(data):
    return AzureApi.get_answer(data["scenario"], "gpt-4")


def add_answer_embeddings(data):
    return AzureApi.get_embedding(data["original_answer"], model="text-embedding-3-small")


enrichers = [
    ("scenario", extract_scenario),
    ("list", extract_list),
    ("original_embeddings", add_original_embeddings),
    ("original_answer", add_answer),
    ("original_answer_embeddings", add_answer_embeddings)
]


def enrich_scenarios(scenarios):
    for scenario in scenarios:
        for key, enricher in enrichers:
            scenario[key] = enricher(scenario)
    return scenarios


def enrich_scenarios_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return enrich_scenarios(data)


def main():
    scenario_dir = 'GPT4Temp0'
    filepath = os.path.join(os.path.dirname(__file__)) # cab add scenario_dir
    filename = 'testing_data_good_take.json'
    input_full_path = os.path.join(filepath, filename)
    enriched_scenarios = enrich_scenarios_from_file(input_full_path)
    output_file = 'enriched_2_' + filename
    output_full_path = os.path.join(filepath, output_file)
    print(output_full_path)
    with open(output_full_path, 'w') as file:
        json.dump(enriched_scenarios, file, indent=4)


if __name__ == "__main__":
    main()