import google.generativeai as genai
import os
import json
import random
import time
# load api key from environment variable
api_key = os.getenv('GEMINI_API_KEY')

for i in range(50):
# Step 1: Read the input file containing the JSON data
    input_file = './restructured_output.json'
    output_file = './selected_users.txt'

    # Convert the string to a dictionary
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Step 2: Randomly select users
    num_users_to_select = 100  # You can adjust this number
    selected_users = random.sample(list(data.keys()), num_users_to_select)

    # Step 3: Create a new dictionary with only the selected users  
    selected_data = {user: data[user] for user in selected_users}
    genai.configure(api_key=api_key)
    with open("instruction.txt", "r") as file:
        input_text = file.read()
    with open("example_char.txt", "r") as file:
        example_char = file.read()
    model = genai.GenerativeModel("gemini-1.5-pro-exp-0827"
      ,generation_config=genai.types.GenerationConfig(
        temperature=2.0,
    ),
    )
    response = model.generate_content(input_text+"\n"+str(selected_users)+"\n"+str(example_char))
    with open('gen_char.txt', 'a') as f:
        f.write(response.text)
        print(response.text)
    if i%2==1:
        time.sleep(60)