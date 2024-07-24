import json
import os
# Define the input and output file paths
input_file_path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "data", "scripts_to_generate_data", "enriched_testing_data_good_take.json")
output_file_path = 'new_enriched_testing_data_good_take.json'

# Load the JSON data from the file
with open(input_file_path, 'r') as file:
    data = json.load(file)

for entry in data:
    scenario = entry['scenario']
    list = entry['list']
    for element in list:
        if element not in scenario:
            list.remove(element)

# Write the updated data back to the file
with open(output_file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("The keys 'original_embeddings' and 'original_answer_embeddings' have been removed.")
