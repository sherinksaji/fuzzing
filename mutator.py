import random
import time
import copy
import string

class Mutator:
    def __init__(self):
        self.prev_output = None

    def __init__(self) -> None:
        pass

    def mutate_number(self, original_number):

        def add_subtract_random_value(n):
            delta = random.randint(1, 10)
            return n + random.choice([-delta, delta])

        def multiply_divide_random_factor(n):

            factor = random.choice([0.5, 2])
            operation = random.choice([lambda x: x * factor, lambda x: x / factor])
            return int(operation(n))

        def flip_random_bit(n):

            bit = 1 << random.randint(0, 31)
            return n ^ bit

        def generate_large_number(n):
            print("generate_large_number")
            return (2**32) - 1

        def generate_small_number(n):
            print("generate_small_number")
            return -((2**32) - 1)
        
        mutators = [
            add_subtract_random_value,
            multiply_divide_random_factor,
            flip_random_bit,
            generate_large_number,
            generate_small_number
        ]

        mutator = mutators[random.randint(0, len(mutators) - 1)]

        return mutator(original_number)

    def mutate_str(self, original_str=''):
        char_digits = string.digits              #'0123456789'
        char_uppercase = string.ascii_uppercase  #'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        char_lowercase = string.ascii_lowercase  #'abcdefghijklmnopqrstuvwxyz'
        char_punc = string.punctuation        #'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        all_chars = char_digits + char_uppercase + char_lowercase + char_punc
        def delete_random_character(s):
            """Returns s with a random character deleted"""
            print('delete')
            if s == "":
                return s

            pos = random.randint(0, len(s) - 1)
            return s[:pos] + s[pos + 1:]

        def insert_random_character(s):
            """Returns s with a random character inserted"""
            print('insert', s)
            pos = random.randint(0, len(s))
            random_character = random.sample(all_chars, 1)[0]
            print(random_character, s[:pos], s[pos:])
            return s[:pos] + random_character + s[pos:]


        def flip_random_character(s):
            """Returns s with a random bit flipped in a random position"""
            print('flip')
            if s == "":
                return s

            try:

                byte_array = bytearray(original_str, 'utf-8')

                # Generate a random bit index from 0 to 7
                bit_index = random.randint(0, 7)

                char_index = random.randint(0, len(s)-1)

                # Flip the specified bit (bit_index) in the byte at position char_index
                byte_array[char_index] ^= 1 << bit_index

                # Convert the bytearray back to a string
                mutated_string = byte_array.decode('utf-8')
                return mutated_string

            except Exception:
                flip_random_character(s)

        def generate_extreme_string(s):
            print('long str')
            long_string = ''.join(random.choice(all_chars) for _ in range(256))
            empty_string = ''
            if random.randint(0,1) == 0:
                return long_string
            return empty_string


        '''
        Randomly choose a mutation method to mutate the string
        '''
        mutators = [
            delete_random_character,
            insert_random_character,
            flip_random_character,
            generate_extreme_string,
        ]

        mutator = mutators[random.randint(0, len(mutators)-1)]
        return mutator(original_str)

    def mutate_arr(self,array):
        return random.choice(array)

    def mutate_byte_list(self, byte_list):
        random.seed(time.time_ns())

        def replace_random_byte(byte_list):
            if byte_list:
                index = random.randint(0, len(byte_list) - 1)
                byte_list[index] = random.randint(0, 255)
            return byte_list

        def add_random_byte(byte_list):
            index = random.randint(0, len(byte_list))
            byte_list.insert(index, random.randint(0, 255))
            return byte_list

        def remove_random_bytes(byte_list):
            if byte_list:
                # Determine how many bytes to remove, at least 1, up to the length of the list
                num_to_remove = random.randint(1, len(byte_list))

                for _ in range(num_to_remove):
                    if (
                        byte_list
                    ):  # Check if list is not empty before attempting to remove
                        index = random.randint(0, len(byte_list) - 1)
                        del byte_list[index]

            return byte_list

        def flip_random_bit(byte_list):
            if not byte_list:
                return byte_list
            byte_index = random.randint(0, len(byte_list) - 1)
            byte_value = byte_list[byte_index]
            bit_position = random.randint(0, 7)
            byte_list[byte_index] = byte_value ^ (1 << bit_position)
            return byte_list

        def havoc(byte_list):

            byte_list.insert(0, 0xFF)
            return byte_list

        def insert1(byte_list):
            byte_list.insert(0, 1)
            return byte_list

        def insert0(byte_list):
            byte_list.insert(0, 0)
            return byte_list

        def extend_with_random_bytes(byte_list):
            num_bytes = random.randint(1, 10)
            byte_list.extend(random.randint(0, 255) for _ in range(num_bytes))
            return byte_list

        def empty(byte_list):
            return []

        # List of mutators
        mutators = [
            insert1,
            insert0,
            replace_random_byte,
            add_random_byte,
            remove_random_bytes,
            flip_random_bit,
            havoc,
            extend_with_random_bytes,
            empty,
        ]

        # Select a random mutator and apply it
        probabilities = [0.110, 0.110, 0.110, 0.113, 0.113, 0.113, 0.111, 0.113, 0.107]
        mutator = random.choices(mutators, probabilities, k=1)[0]
        # print(mutator)
        # probability = random.random()
        # if probability < 0.1:
        #     return empty()
        return mutator(byte_list)

    def mutate(self, attributes):
        '''
        Take in A list of attributes to mutate, mutate one attribute at a time with equal probability
        '''


        mutated_pos = random.randint(0, len(attributes)-1)

        mutated_input = copy.deepcopy(attributes)

        if isinstance(attributes[mutated_pos], int):
            mutated_input[mutated_pos] = self.mutate_number(attributes[mutated_pos])
        elif isinstance(attributes[mutated_pos], str):
            mutated_input[mutated_pos] = self.mutate_str(attributes[mutated_pos])

        return mutated_input


# Test
# mutator = Mutator()
# byte_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
# print(byte_list)
# mutated = mutator.mutate_byte_list(byte_list)
# print(mutated)


# byte_string = bytes([65, 66, 67, 68, 69])
# print(byte_string)
# bs = mutator.mutate_bytestring(byte_string)
# print(bs)

# byte_array = bytearray([65, 66, 67, 68, 69])
# print(byte_array)
# ba = mutator.mutate_bytearray(byte_array)
# print(ba)
