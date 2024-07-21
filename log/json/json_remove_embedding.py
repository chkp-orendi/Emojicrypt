import json

# Define the input and output file paths
input_file_path = 'tmp.json'
output_file_path = 'new_tmp.json'

# Load the JSON data from the file
with open(input_file_path, 'r') as file:
    data = json.load(file)

# Process the data to remove the specified keys
for entry in data.get('data', []):
    entry.pop('original_embeddings', None)
    entry.pop('original_answer_embeddings', None)

# Write the updated data back to the file
with open(output_file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("The keys 'original_embeddings' and 'original_answer_embeddings' have been removed.")
