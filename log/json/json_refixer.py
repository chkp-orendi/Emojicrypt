import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../libraries'))
import AzureApi


def add_original_embeddings(data):
    return AzureApi.get_embedding(data["scenario"], model="text-embedding-3-small")


def add_answer(data):
    return AzureApi.get_answer(data["scenario"], "gpt-4")
    return data


def add_answer_embeddings(data):
    return AzureApi.get_embedding(data["original_answer"], model="text-embedding-3-small")


enrichers = [
    ("original_embeddings", add_original_embeddings),
    ("original_answer", add_answer),
    ("original_answer_embeddings", add_answer_embeddings)
]


def enrich_scenarios(scenarios):

    for scenario in scenarios:
        for key, enricher in enrichers:
            if key not in scenario.keys():
                scenario[key] = enricher(scenario)
    return scenarios


def enrich_scenarios_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return enrich_scenarios(data)


def main():
    scenario_dir = 'GPT4Temp0'
    filepath = os.path.join(os.path.dirname(__file__), scenario_dir)
    filename = 'generated_data_1.json'
    input_full_path = os.path.join(filepath, filename)
    enriched_scenarios = enrich_scenarios_from_file(input_full_path)
    output_file = 'enriched_' + filename
    output_full_path = os.path.join(filepath, output_file)
    with open(output_full_path, 'w') as file:
        json.dump(enriched_scenarios, file, indent=4)


if __name__ == "__main__":
    main()
