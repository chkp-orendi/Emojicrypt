import json
import os
# Define the input and output file paths
input_file_path = os.path.join("C:\\Users", "orendi", "Documents", "EmojiCrypt-main", "Emojicrypt", "data", "scripts_to_generate_data", "enriched_testing_data_good_take.json")
output_file_path = 'new_enriched_testing_data_good_take_2.json'

# Load the JSON data from the file
with open(input_file_path, 'r') as file:
    data = json.load(file)

for entry in data[0:1]:
    scenario = entry['scenario']
    list_elements = entry['list']
    for element in list_elements:
        elements_to_remove = []
        if element not in scenario:
            elements_to_remove.append(element)
    entry['list'] = [element for element in list_elements if element in scenario]
# Write the updated data back to the file
with open(output_file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("done")
