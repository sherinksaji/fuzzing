import string
import random

FLIP_RATIO = 0.1  # 1% ratio of bit flips
FLIP_ARRAY = [1, 2, 4, 8, 16, 32, 64, 128]

MAGIC_VALS = [
    [0xFF],
    [0x7F],
    [0x00],
    [0xFF, 0xFF],  # 0xFFFF
    [0x00, 0x00],  # 0x0000
    [0xFF, 0xFF, 0xFF, 0xFF],  # 0xFFFFFFFF
    [0x00, 0x00, 0x00, 0x00],  # 0x80000000
    [0x00, 0x00, 0x00, 0x80],  # 0x80000000
    [0x00, 0x00, 0x00, 0x40],  # 0x40000000
    [0xFF, 0xFF, 0xFF, 0x7F],  # 0x7FFFFFFF
]

class Mutator:

    def __init__(self):
        self.mutators = [
            self.flip_bit,
            self.flip_bit_2,
            self.flip_bit_4,
            self.flip_byte,
            self.flip_byte_16,
            self.flip_byte_32,
            self.add_random_char,
            self.add_random_chars
        ]

        self.non_ascii_mutators=[
            self.insert_non_ascii_char,
            self.insert_non_ascii_chars,
            self.bit_flip,
            self.mutate_str,
            self.shorten_str,
            self.lengthen_str,
            self.mutate_bytestring,
            self.shorten_bytestring,
            self.lengthen_bytestring,
            self.mutate_number,
            self.mutate_bytearray,
            self.shorten_bytearray,
            self.lengthen_bytearray
        ]
        
    def flip_bit(self, text):
        result = ""
        n=len(text)
        position= random.randint(0, n)
        for char in text:
            if char.isalnum():
                ascii_value = ord(char)
                flipped_ascii_value = ascii_value ^ (1 << position)
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
    
    def add_random_chars(self, text):
        num_chars=random.randint(0, 8)
        for _ in range(num_chars):
            text = self.add_random_char(text)
        return text
    
    ####################################################################################
    
    def insert_non_ascii_char(self, text):
        position = random.randint(0, len(text))
        char = chr(random.randint(128, 255))  # Generate a random non-ASCII character
        return text[:position] + char + text[position:]
    
    def insert_non_ascii_chars(self, text):
        num_chars=random.randint(0, 8)
        for _ in range(num_chars):
            text = self.insert_non_ascii_char(text)
        return text

    def bit_flip(self, byte):
        return byte ^ random.choice(FLIP_ARRAY)

    def magic(self, data, idx):
        picked_magic = random.choice(MAGIC_VALS)
        offset = 0
        for m in picked_magic:
            data[idx + offset] = m
            offset += 1

    def mutate_str(self, input_str):
        data = list(input_str.encode("utf-16"))
        # for byte in data:
        #     print(byte, end=' ')
        # print("\n")
        flips = int(len(data) * FLIP_RATIO)
        flip_indexes = random.choices(range(0, len(data) - 6), k=flips)
        # print(flips, flip_indexes)
        methods = [0, 1]
        for idx in flip_indexes:
            method = random.choice(methods)
            if method == 0:
                data[idx] = self.bit_flip(data[idx])
            else:
                self.magic(data, idx)
        # for byte in data:
        #     print(byte, end=' ')
        # print("\n")
        # print(bytearray(data).decode("utf-16"), "\n\n")
        return bytearray(data).decode("utf-16")

    def decide_reduction_ratio(self, input_obj):
        """
        Decide the reduction ratio based on the length of the input string,
        ensuring a minimum meaningful reduction for very short strings.
        Args: input_str (str): The input string to determine the reduction ratio for.
        Returns: float: The reduction ratio to use, or a special value indicating a minimum reduction for very short strings.
        """
        length = len(input_obj)
        if length <= 1:
            # For a single character or empty string, no reduction is possible
            return 0
        elif length <= 4:
            # For very short strings, reduction by a fixed minimum (e.g., removing one character) might be more appropriate
            return 1 / length  # Ensures at least one character is removed
        elif 4 < length < 10:
            # Short strings can have a smaller reduction ratio
            return 0.2
        elif 10 <= length < 50:
            # Moderate length strings can have a moderate reduction ratio
            return 0.3
        elif 50 <= length < 100:
            # Longer strings can afford a larger reduction ratio
            return 0.4
        else:
            # Very long strings can have the largest reduction ratio
            return 0.5

    def decide_addition_ratio(self, input_obj):
        """
        Decide the addition ratio based on the length of the input string,
        aiming to balance the additions so as not to overwhelm short strings
        and to proportionally extend longer strings.
        Args: input_str (str): The input string to determine the addition ratio for.
        Returns: float: The addition ratio to use, carefully calibrated based on string length.
        """
        length = len(input_obj)
        if length <= 1:# For a single character or empty string, being conservative with additions
            return 1  # Doubling or adding one more character might be meaningful
        elif length <= 4:# For very short strings, being slightly aggressive to make a noticeable difference
            return 0.75  # Add up to 75% more characters
        elif 4 < length < 10:# Short strings can handle a moderate addition ratio
            return 0.5  # Add up to 50% more characters
        elif 10 <= length < 50:# As strings get longer, a smaller addition ratio can still result in significant growth
            return 0.3
        elif 50 <= length < 100:# For longer strings, further minimize the addition ratio to maintain coherence
            return 0.2
        else:
            # Very long strings should have the smallest addition ratio
            return 0.1  # Add up to 10% more characters to maintain readability and coherence

    def shorten_str(self, input_str, reduction_ratio="auto decide"):
        if reduction_ratio == "auto decide":
            reduction_ratio = self.decide_reduction_ratio(input_str)
        if reduction_ratio < 0 or reduction_ratio > 1:
            raise ValueError("Reduction ratio must be between 0 and 1")
        length_to_remove = int(len(input_str) * reduction_ratio)
        for _ in range(length_to_remove):
            if len(input_str) > 0:# Randomly remove a character
                remove_index = random.randint(0, len(input_str) - 1)
                input_str = input_str[:remove_index] + input_str[remove_index + 1 :]
        return input_str

    def lengthen_str(self, input_str, addition_ratio="auto decide"):
        if addition_ratio == "auto decide":
            addition_ratio = self.decide_addition_ratio(input_str)
        length_to_add = int(len(input_str) * addition_ratio)
        for _ in range(length_to_add):# Randomly duplicate a character
            if len(input_str) > 0:
                add_index = random.randint(0, len(input_str) - 1)
                input_str = (
                    input_str[:add_index] + input_str[add_index] + input_str[add_index:]
                )
        return input_str

    def mutate_bytestring(self, byte_string, mutation_type="invert", mutation_ratio="auto decide"): #Mutate a byte string by inverting a ratio of its bytes, specified by mutation_ratio.
        if mutation_ratio == "auto decide":
            mutation_ratio = self.decide_reduction_ratio(byte_string)
        if not byte_string:
            # Handle empty byte string case
            return byte_string
        byte_array = bytearray(byte_string)  # Convert to bytearray for ease of mutation
        n = len(byte_array)
        n_mutate = max(1, int(n * mutation_ratio)) # Ensure at least one byte is mutated
        if mutation_type == "invert":
            # Randomly select bytes to mutate based on the specified ratio
            indexes_to_mutate = random.sample(range(n), n_mutate)
            for i in indexes_to_mutate:
                byte_array[i] = ~byte_array[i] & 0xFF  # Invert the byte
            return bytes(byte_array)  # Convert back to bytes
        elif mutation_type == "shuffle":
            byte_list = list(byte_string)
            random.shuffle(byte_list)
            return bytes(byte_list)
        else:
            raise ValueError("Unsupported mutation type")

    def shorten_bytestring(self, byte_string, reduction_ratio=0.1):
        """Reduce the length of a byte string by a percentage."""
        if reduction_ratio == "auto decide":
            reduction_ratio = self.decide_reduction_ratio(byte_string)
        new_length = int(len(byte_string) * (1 - reduction_ratio))
        return byte_string[:new_length]

    def lengthen_bytestring(self, byte_string, addition_ratio="auto decide"): #Attempt to increase the length of a byte string by duplicating random parts of it.
        if addition_ratio == "auto decide":
            addition_ratio = self.decide_addition_ratio(byte_string)
        if not isinstance(byte_string, bytes):
            raise ValueError("Input must be a byte string")
        length_to_add = int(len(byte_string) * (addition_ratio))
        additions = [random.choice(byte_string) for _ in range(length_to_add)]
        # For simplicity, appending at the end. Could be made more complex by inserting at random positions
        return byte_string + bytes(additions)

    def mutate_number(self, number):
        if isinstance(number, int):
            return number ^ random.choice(FLIP_ARRAY)
        elif isinstance(number, float):
            return number + random.uniform(-1, 1)
        else:
            raise TypeError("Unsupported number type")

    def mutate_bytearray(self, byte_array, mutation_ratio=0.1): #Mutate a bytearray by inverting a ratio of its bytes.
        n = len(byte_array)
        n_mutate = max(1, int(n * mutation_ratio)) # Ensure at least one byte is mutated
        indexes_to_mutate = random.sample(range(n), n_mutate)
        for i in indexes_to_mutate:
            byte_array[i] = ~byte_array[i] & 0xFF  # Invert the byte
        return byte_array

    def shorten_bytearray(self, byte_array, reduction_ratio="auto decide"): #Reduce the length of a bytearray by a percentage.
        if reduction_ratio == "auto decide":
            reduction_ratio = self.decide_reduction_ratio(byte_array)
        new_length = int(len(byte_array) * (1 - reduction_ratio))
        del byte_array[new_length:]  # Delete bytes from new_length to the end
        return byte_array

    def lengthen_bytearray(self, byte_array, addition_ratio="auto decide"): #Increase the length of a bytearray by duplicating random parts of it.
        if addition_ratio == "auto decide":
            addition_ratio = self.decide_addition_ratio(byte_array)
        length_to_add = int(len(byte_array) * addition_ratio)
        additions = [random.choice(byte_array) for _ in range(length_to_add)]
        byte_array.extend(additions)
        return byte_array
    

