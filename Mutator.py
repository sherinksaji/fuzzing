import string
import random

class Mutator:

    def __init__(self) -> None:
        self.mutators = [
            self.flip_bit,
            self.flip_bit_general,
            self.flip_bit_2,
            self.flip_bit_4,
            self.flip_byte,
            self.flip_byte_16,
            self.flip_byte_32
        ]
        
    def flip_bit(self, text: str, n: int) -> str:
        result = ""
        for char in text:
            if char.isalnum():
                ascii_value = ord(char)
                flipped_ascii_value = ascii_value ^ (1 << n)
                # Ensure the ASCII value is within the range of printable characters
                if flipped_ascii_value < 32 or flipped_ascii_value > 126:
                    flipped_ascii_value = (flipped_ascii_value % 95) + 32
                result += chr(flipped_ascii_value)
            else:
                result += char
        return result
    
    def flip_bit_general(self, text: str, n: int, k: int, stepover: int) -> str:
        result = ""
        for i in range(0, len(text), k + stepover):
            chunk = text[i:i + k]
            flipped_chunk = ""
            for j in range(len(chunk)):
                if j < len(chunk) and chunk[j].isalnum():
                    ascii_value = ord(chunk[j])
                    flipped_ascii_value = ascii_value ^ (1 << ((j + n) % k))
                    # Ensure the ASCII value is within the range of printable characters
                    if flipped_ascii_value < 32 or flipped_ascii_value > 126:
                        flipped_ascii_value = (flipped_ascii_value % 95) + 32
                    flipped_chunk += chr(flipped_ascii_value)
                else:
                    flipped_chunk += chunk[j]
            result += flipped_chunk
        return result
    
    def flip_bit_2(self, text: str) -> str:
        return self.flip_bit_general(text, 0, 2, 1)
    
    def flip_bit_4(self, text: str) -> str:
        return self.flip_bit_general(text, 0, 4, 1)
    
    def flip_byte(self, text: str) -> str:
        return self.flip_bit_general(text, 0, 8, 8)
    
    def flip_byte_16(self, text: str) -> str:
        return self.flip_bit_general(text, 0, 16, 8)
    
    def flip_byte_32(self, text: str) -> str:
        return self.flip_bit_general(text, 0, 32, 8)


# Test the class functions
mutator = Mutator()
text = "helErrtyrurb"  # Example text to test
print("Original text:", text)
for method in mutator.mutators:
    if method.__name__ == "flip_bit":
        # For flip_bit(), pass both text and n
        print(method.__name__, ":", method(text,0))
    elif method.__name__ == "flip_bit_general":
        # For flip_bit_general(), pass all required arguments
        print(method.__name__, ":",method(text,0,2,1))
    else:
        # For other methods, pass only text
        print(method.__name__, ":", method(text))
