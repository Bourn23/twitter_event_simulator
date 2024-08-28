import json

def filter_json(input_file, output_file):
    # Texts to filter out
    filter_texts = [
        "This Post was deleted by the Post author. Learn more",
        "You're unable to view this Post because this account owner limits who can view their Posts. Learn more",
        "This Post is from a suspended account. Learn more"
    ]

    # Read the input JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # If UTF-8 fails, try with 'utf-8-sig' (to handle BOM)
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

    # Filter out elements with the specified texts
    def should_keep(item):
        if isinstance(item, dict):
            tombstone = item.get("tombstone", {})
            if isinstance(tombstone, dict):
                text_obj = tombstone.get("text", {})
                if isinstance(text_obj, dict):
                    text = text_obj.get("text")
                    return text not in filter_texts
        return True

    filtered_data = [item for item in data if should_keep(item)]

    # Write the filtered data to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)

    print(f"Filtered JSON has been written to {output_file}")

# Usage
input_file = "tweets_2019.json"
output_file = "tweets_2019_Clean.json"
filter_json(input_file, output_file)