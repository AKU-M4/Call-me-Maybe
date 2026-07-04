
def whisper_cipher(text: str, shift: int) -> str:
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift_char = (ord(char) - base + shift)
            shifted_char = shift_char % 26 + base
            print(f"({shift_char}), ({shifted_char})")
            result.append(chr(shifted_char))
        else:
            result.append(char)
    return "".join(result)

def shadow_merge(list1: list[int], list2: list[int]) -> list[int]:
    merged_lists = list1 + list2

    return sorted(merged_lists)



def main():
    test_1 = whisper_cipher("hey there", 5);
    #test_2 = whisper_cipher("xyz", -5);
    #test_3 = whisper_cipher("YwsX-ndkren", 24);
    #print(f"{test_1}")
    print(f"{shadow_merge([], [6, 4, 6])}")

if __name__ == "__main__":
    main()