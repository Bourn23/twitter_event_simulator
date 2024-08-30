import re
import json

# Function to parse the text and convert it into JSON
def parse_text_to_json(text):
    characters = []
    
    # Enhanced regex pattern to capture key-value pairs, including Unicode characters and emojis
    field_pattern = re.compile(r'"(\w+)"\s*:\s*"(.*?)"', re.UNICODE | re.DOTALL)
    tweet_pattern = re.compile(r'"tweets"\s*:\s*\[\s*((?:"(?:[^"\\]|\\.)*"(?:\s*,\s*)?)+)\s*\]', re.DOTALL | re.UNICODE) # from claude

    # Splitting the content by assuming each character block starts with a field like aesop_id
    blocks = re.split(r'(?="aesop_id")', text)

    for block in blocks:
        if block.strip():  # Ensuring that the block is not empty
            # Extract fields using regex
            fields = dict(field_pattern.findall(block))

            # Extract tweets
            tweets_section = tweet_pattern.search(block)
            if tweets_section:
                tweets_raw = tweets_section.group(1)
                # Modified to capture tweets, handling multiline and special characters like links and emojis
                tweets = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', tweets_raw, re.UNICODE | re.DOTALL)
                fields["tweets"] = [tweet.strip() for tweet in tweets]
            else:
                print("no match for tweets", block)

            # Convert entourage_size and entourage if they exist
            if "entourage_size" in fields:
                fields["entourage_size"] = int(fields["entourage_size"])
            if "entourage" in fields:
                try:
                    fields["entourage"] = json.loads(fields["entourage"])
                except json.JSONDecodeError:
                    fields["entourage"] = []

            characters.append(fields)

    return characters

# Read the text file content
with open('gen_char.txt', 'r', encoding='utf-8') as file:
    text_content = file.read()

# Parse the text to JSON
parsed_data = parse_text_to_json(text_content)

# Save the JSON data into a file
with open('characters.json', 'w', encoding='utf-8') as json_file:
    json.dump(parsed_data, json_file, indent=4, ensure_ascii=False)

print("Conversion completed! JSON file saved as 'characters.json'.")