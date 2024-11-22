
import google.generativeai as genai
import os
import json
import random
import time
import typing_extensions as typing

class Person(typing.TypedDict):
    aesop_id: str
    name: str
    user_type: str  # e.g., "influencer" or "normal person"
    Job: str
    age: int
    gender: str  # e.g., "Male", "Female", "Non-binary"
    race: str
    nationality: str
    entourage_size: int
    entourage: list[str]
    bio: str
    tweets: list[str]

# Initialize a list to collect all responses
all_responses = []

for i in range(150):
    # Step 1: Read the input file containing the JSON data
    input_file = './restructured_output.json'

    # Read the data from the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # print(data)

    # Step 2: Randomly select users (Uncomment the next two lines if you want to select random users)
    num_users_to_select = 5
    selected_users = random.sample(list(data.keys()), num_users_to_select)
    # print(selected_users)
    selected_users = dict((k, data[k]) for k in selected_users if k in data)


    # selected_users = data[selected_users]
    # For now, we'll use all users
    # selected_users = data
    print(selected_users)

    # Step 3: Configure the generative AI model
    genai.configure(api_key="---")
    with open("instruction.txt", "r", encoding='utf-8') as file:
        input_text = file.read()
    with open("example_char.txt", "r", encoding='utf-8') as file:
        example_char = file.read()
    model = genai.GenerativeModel(
        "gemini-1.5-pro",
        generation_config=genai.types.GenerationConfig(
            temperature=0.5,
            response_mime_type="application/json",
            response_schema=list[Person]
        ),
    )


    # Construct the prompt
    prompt = (
        f"{input_text}\n{selected_users}\n"
        "Now here are the characters you have created thus far. "
        "Please make sure the people and the tweets are not too similar to each other.\n"
        f"{example_char}"
    )

    # Count tokens
    response = model.count_tokens(prompt)
    print(f"Prompt Token Count: {response.total_tokens}")

    # Generate content
    response = model.generate_content(prompt)
    print(response)
    response_data = response._result.candidates[0].content.parts[0].text  # No need to parse, it's already a Python list
    
    # Append the response data to the list of all responses
    all_responses.extend(response_data)

    with open(f'response_{i}.json', 'w', encoding='utf-8') as f:
        json.dump(response_data, f, ensure_ascii=False, indent=4)

    # Optionally, update 'example_char.txt' for the next iteration
    with open('example_char.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(response_data, ensure_ascii=False, indent=4))
        f.write('\n')

    # If needed, update 'example_char.txt' for the next iteration

    # Sleep every other iteration to comply with rate limits
    if i % 2 == 1:
        time.sleep(70)

# After the loop, write all responses to a single JSON file
with open('all_responses.json', 'w', encoding='utf-8') as f:
    json.dump(all_responses, f, ensure_ascii=False, indent=4)