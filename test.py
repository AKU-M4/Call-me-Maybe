import json

def main():
    with open("file.json", "w") as f,  open("test.json", "r") as t:
        data = json.load(t,)
        json.dump(data,f, indent=4)
        print(data)



if __name__ == "__main__":
    main()