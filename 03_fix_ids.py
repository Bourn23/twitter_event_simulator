import json
import uuid
import random

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

        # also add polarity/subjectivity to the users it's a random value between -1 and 1 
        ## This is a quick fix, do not use this in production
        character["polarity"] = round(random.uniform(0, 1), 1)
        character["subjectivity"] = round(random.uniform(0, 1), 1)


    return characters, id_map

def fix_duplicate_ids(json_file_path, output_file_path):
    # Load the parsed JSON data
    with open(json_file_path, 'r', encoding='utf-8-sig') as file: # for parsing Core_characters.json
    # with open(json_file_path, 'r', encoding='utf-8') as file:
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
# json_file_path = 'sep2_data_Characters_core.json' # change the encoding for this one
# json_file_path = 'sep2_data_Characters.json'
# json_file_path = 'sep2_good_org.json' ## NOTE: merge the two organization files into total_organizations.json
# json_file_path = 'Organizations_bad.json' ## NOTE: merge the two organization files into total_organizations.json
json_file_path = 'data_characters_basic_borna.json'
# Output file path for the fixed JSON
output_file_path = 'sep2_basic_characters_fixed_ids.json'

# Run the process to fix duplicate IDs
fix_duplicate_ids(json_file_path, output_file_path)

"""
Bad organizations
Old ID: HeliexpressLTD_PR -> New ID: 60ae02d5-681b-4add-a08e-424c0d858069
Old ID: ArkhangelskBiz -> New ID: 5bbd4c3d-f90a-4ba7-9654-eeb89bb8ec06
Old ID: ArcticDevCouncil -> New ID: f9a4c08a-f18c-471d-a121-c3d7bc6acc1c
Old ID: NorthernTourismBoard -> New ID: da196436-dad2-4938-a8c8-9a425e2cf908
Old ID: org_heliexpress -> New ID: 50735df6-ed02-4242-85a9-4deed9c3e569
Old ID: org_MFA_russia -> New ID: d0f33952-dfd6-44f2-b509-1d802d09de85
Old ID: heliexpress_ltd_pr -> New ID: 4d1794cb-1d8b-41f1-8b1c-c27701d7bda1
Old ID: arkhangelsk_oblast_tourism_bureau -> New ID: 9fa4ed49-fe72-4d99-87ff-133cf62ac579
Old ID: russian_federation_ministry_of_economic_development -> New ID: 9e1b40ee-af3b-4046-a437-54687984d0b1

Good organizations
Old ID: org_norway_mfa -> New ID: f5cd9c28-771e-4e86-a402-c7b7e290635a
Old ID: org_mfa_russia -> New ID: dd76c5f7-bcbc-4644-a004-836693561dc9
Old ID: org_russia_mfa -> New ID: f5c2e0b3-9a64-4d24-9018-9e4c91c70766
Old ID: org_norwegian_ministry_of_foreign_affairs -> New ID: d86f6cfa-1b2b-4b12-b41b-a7ea247d9d38
Old ID: org_russian_ministry_of_foreign_affairs -> New ID: 1576c28a-5d46-44a0-b6b8-f11dc4e7d170
Old ID: org_Heliexpress_LTD -> New ID: 1e3ae17e-2c8b-4cf9-876c-9ab56dfa6eb3
Old ID: org_MFA_Russia -> New ID: 0ba83650-ca1a-4cb7-b4e4-aa1d6dbb9739
Old ID: org_NorwayMFA -> New ID: 7f9e8edd-fc22-45fc-aff0-7be983982e67
Old ID: org_heliexpress_ltd -> New ID: 9f17a30e-166e-4aa9-8e35-bea49505bdb1
Old ID: org_norwaymfa -> New ID: 3417a470-d4e8-4e88-93b9-a5eac46d9865
"""