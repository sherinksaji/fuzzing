import string
import random

class Mutator:

    def __init__(self):
        self.mutators = [
            self.flip_bit,
            self.flip_bit_general,
            self.flip_bit_2,
            self.flip_bit_4,
            self.flip_byte,
            self.flip_byte_16,
            self.flip_byte_32,
            self.add_random_char,
            self.add_random_chars,
            self.insert_non_ascii_char,
            self.insert_non_ascii_chars
        ]

    def generate_random_str(self,len_limit):
        characters = string.ascii_letters + string.digits + string.punctuation
        result_str = ''.join(random.choice(characters) for _ in range(len_limit))
        return result_str
        
    def flip_bit(self, text, n):
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
    
    def flip_bit_general(self, text, n, k, stepover):
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
    
    def flip_bit_2(self, text):
        return self.flip_bit_general(text, 0, 2, 1)
    
    def flip_bit_4(self, text):
        return self.flip_bit_general(text, 0, 4, 1)
    
    def flip_byte(self, text):
        return self.flip_bit_general(text, 0, 8, 8)
    
    def flip_byte_16(self, text):
        return self.flip_bit_general(text, 0, 16, 8)
    
    def flip_byte_32(self, text):
        return self.flip_bit_general(text, 0, 32, 8)
    
    def add_random_char(self, text):
        position = random.randint(0, len(text))
        char = random.choice(string.ascii_letters + string.digits + string.punctuation)
        return text[:position] + char + text[position:]
    
    def add_random_chars(self, text, num_chars):
        for _ in range(num_chars):
            text = self.add_random_char(text)
        return text
    
    def insert_non_ascii_char(self, text):
        position = random.randint(0, len(text))
        char = chr(random.randint(128, 255))  # Generate a random non-ASCII character
        return text[:position] + char + text[position:]
    
    def insert_non_ascii_chars(self, text, num_chars):
        for _ in range(num_chars):
            text = self.insert_non_ascii_char(text)
        return text
