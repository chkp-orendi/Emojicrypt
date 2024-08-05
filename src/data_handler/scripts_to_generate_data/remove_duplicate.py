import json




def process_json_elements(file_path):
    # Open the JSON file
    with open(file_path, 'r') as file:
        # Load the JSON data
        data = json.load(file)
        
        # Iterate over each element in the JSON data
        for element in data:
            # Process each element (for example, print it)
            scenario = element['scenario']
            list = element['list']
            new_list = []
            for word in list:
                word = word.strip()
                if word in scenario:
                    new_list.append(word)

            element['list'] = new_list 
        

        with open('C:\\Users\\orendi\\Documents\\EmojiCrypt-main\\Emojicrypt\\data\\scripts_to_generate_data\\29-07-good-take.json', 'w') as file:
            json.dump(data, file, indent=4)
# Example usage
process_json_elements('C:\\Users\\orendi\\Documents\\EmojiCrypt-main\\Emojicrypt\\data\\scripts_to_generate_data\\2024-07-24_12-00-00_dataset_good_take.json')