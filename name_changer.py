import json
import random
from names_generator import generate_name

# Function to randomly assign a new name and update the bio
def assign_new_name(entry):
    new_name = generate_name(style='capital')
    # Replace the name in the entry
    entry["name"] = new_name
    # Update the bio to start with the new name
    first_sentence_end = entry["bio"].find('.')
    if first_sentence_end != -1:
        entry["bio"] = new_name + entry["bio"][len(entry["name"]):]
    else:
        entry["bio"] = new_name + " " + entry["bio"][len(entry["name"]):]
    print(f"Updated name: {new_name}")
    return entry

# Load your JSON data
with open('basic_characters_fixed_ids.json', 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

# Process each entry in the JSON data
for entry in data:
    print(entry)
    entry = assign_new_name(entry)

# Save the updated JSON data
with open('data_characters_basic_borna.json', 'w' ,encoding='utf-8-sig') as file:
    json.dump(data, file, indent=4)

print("Names have been updated and saved to data_updated.json")
