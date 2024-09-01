import json
import random
# Load the characters_fixed.json file
with open('characters_fixed_ids.json', 'r') as f:
    users_data = json.load(f)

with open('Characters_core.json', 'r') as f:
    core_users = json.load(f)

with open('Characters_basic.json', 'r') as f:
    basic_users = json.load(f)

with open('bad_org.json', 'r') as f:
    organization_users = json.load(f)

# mix users_data and users_data_2
users_data += users_data_2

# Initialize lists for core, basic, and organization users
core_users = []
basic_users = []
organization_users = []

# Classify users into core, basic, and organization categories #TODO: fix this later.
# for user in users_data:
#     if user['type'] == "Organization":
#         organization_users.append(user)
#     elif user['type'] == "Influential Person":
#         core_users.append(user)
#     else:
#         basic_users.append(user)

# Classify users into core, basic, and organization categories randomly since we don't have a user type yet
for user in users_data:
    user_type = random.choices(["Basic", "Core", "Organization"], weights=[25, 5, 5], k=1)[0]
    if user_type == "Organization":
        organization_users.append(user)
    elif user_type == "Core":
        core_users.append(user)
    else:
        basic_users.append(user)

# Save the split data into three separate JSON files
with open('core_users.json', 'w') as f:
    json.dump(core_users, f, indent=4)

with open('basic_users.json', 'w') as f:
    json.dump(basic_users, f, indent=4)

with open('organization_users.json', 'w') as f:
    json.dump(organization_users, f, indent=4)

print(f"Users split and saved into core_users.json ({len(core_users)} users), "
      f"basic_users.json ({len(basic_users)} users), and "
      f"organization_users.json ({len(organization_users)} users).")