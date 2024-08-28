import json
import glob
import os

def combine_json_files(output_filename):
    combined_data = []

    # Get all files matching the pattern
    input_files = glob.glob("tweets_*.json")

    # Sort the files to ensure consistent order
    input_files.sort()

    # Read each file and combine the data
    for file in input_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    combined_data.append(data)
        except UnicodeDecodeError:
            # If UTF-8 fails, try with 'latin-1' encoding
            with open(file, 'r', encoding='latin-1') as f:
                data = json.load(f)
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    combined_data.append(data)
        print(f"Processed: {file}")

    # Write the combined data to the output file
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)

    print(f"Combined {len(input_files)} files into {output_filename}")

# Run the function
combine_json_files("tweets_2019.json")