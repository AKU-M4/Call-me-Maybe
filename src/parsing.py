import json
import numpy as np
import random
import os

# test = [("name1", "adam kaid salim"),("name2", "ali kaid salim"), ("name3", "sarah akerkaoi")
#         ]
random.seed(2)



# def main() -> None:
    
#     listed_data: list[words] = []
#     with open("../data/input/function_calling_tests.json", "r") as f:
#         data = load(f)
    
#     dict_names = {k: v.split(' ') for k, v in test}
#     with open("file.json", "w") as jf:
#         dump(dict_names, jf)
#     print("\n=== Testing dict comprehessions ===\n")
#     print(dict_names, "\n")
#     print("=" * 40)

# Loading our json data

def tokenizing(prompt: str, filename: str) -> None:
    # 1. Start with an empty dictionary by default
    json_data = {}
    
    # 2. Check if file exists AND has content (> 0 bytes) before loading
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            with open(filename, "r") as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {filename} contains invalid JSON. Starting fresh.")
    else:
        print(f"File {filename} not found or is empty. Creating a new one.")

    # 3. Process the words
    words = prompt.split(" ")
    for word in words:
        if word not in json_data:
            new_id = random.randint(1, 999)

            while new_id in json_data.values():
                new_id = random.randint(1, 999)
            
            json_data[word] = new_id
    
    # 4. Save back to the file using the correct variable 'filename'
    with open(filename, "w") as json_f:
        json.dump(json_data, json_f, indent=4)
        
    print(json_data)


if __name__ == "__main__":
    tokenizing("how about the calculation of 10 and 3?", "file.json")
