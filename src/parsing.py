from json import load, dump
import numpy as np
import random

random.seed(2)

test = [("name1", "adam kaid salim"),("name2", "ali kaid salim"), ("name3", "sarah akerkaoi")
        ]

def main() -> None:
    
    listed_data: list[words] = []
    with open("../data/input/function_calling_tests.json", "r") as f:
        data = load(f)
    
    dict_names = {k: v.split(' ') for k, v in test}
    with open("file.json", "w") as jf:
        dump(dict_names, jf)
    print("\n=== Testing dict comprehessions ===\n")
    print(dict_names, "\n")
    print("=" * 40)

word_vocab = {}

def tokenizing(prompt: str) -> None:
    words = prompt.split(" ")

    for word in words:
        if word not in word_vocab:
            new_id = random.randint(1, 999)
            
            while new_id in word_vocab.values():
                new_id = random.randint(1, 999)
            word_vocab[word] = new_id
    print(word_vocab)
    word_ids = list(word_vocab.values())
    print(f"Words IDs: {word_ids}")




if __name__ == "__main__":
    main()
    tokenizing("what is the sum of 1 and 2?")