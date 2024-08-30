import json
import uuid

def assign_unique_ids(characters):
    seen_ids = set()
    id_map = {}

    for character in characters:
        original_id = character["aesop_id"]
        
        # If the id is already seen, we need to generate a new unique one
        # if original_id in seen_ids:
        new_id = str(uuid.uuid4())
        seen_ids.add(new_id)
        while new_id in seen_ids:
            new_id = str(uuid.uuid4())
        character["aesop_id"] = new_id
        id_map[original_id] = new_id

    return characters, id_map

def fix_duplicate_ids(json_file_path, output_file_path):
    # Load the parsed JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        characters = json.load(file)

    # Assign new unique IDs to characters with duplicate aesop_id
    updated_characters, id_map = assign_unique_ids(characters)

    # Save the updated JSON data into a new file
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(updated_characters, json_file, indent=4, ensure_ascii=False)

    # Report the changes
    if id_map:
        print("Duplicate IDs found and fixed:")
        for old_id, new_id in id_map.items():
            print(f"Old ID: {old_id} -> New ID: {new_id}")
    else:
        print("No duplicate IDs were found.")

# File path to the JSON file containing parsed character data
json_file_path = 'characters.json'
# Output file path for the fixed JSON
output_file_path = 'characters_fixed.json'

# Run the process to fix duplicate IDs
fix_duplicate_ids(json_file_path, output_file_path)