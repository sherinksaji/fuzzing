import copy
import random
import string


class Mutator():
    """
    Mutator is capable to mutate number, string

    """
    def __init__(self):
        pass

    def mutate_number(self, original_number):

        def add_subtract_random_value(n):
            """Returns n plus or minus a random value"""
            delta = random.randint(1, 10)  # Adjust this range as needed
            return n + random.choice([-delta, delta])

        def multiply_divide_random_factor(n):
            """Returns n multiplied or divided by a small factor"""
            factor = random.choice([0.5, 2])  # Example factors
            operation = random.choice([lambda x: x*factor, lambda x: x/factor])
            return int(operation(n))
        def flip_random_bit(n):
            """Returns n with a random bit flipped"""
            bit = 1 << random.randint(0, 31)  # For a 32-bit integer
            return n ^ bit

        def generate_large_number(n):
            """Returns a very large number (2 ** 32) - 1"""
            return (2 ** 32) - 1

        def generate_small_number(n):
            """Returns a very small number -((2 ** 32) - 1)"""
            return -((2 ** 32) - 1)


        mutators = [
            add_subtract_random_value,
            multiply_divide_random_factor,
            flip_random_bit,
            generate_large_number,
            generate_small_number
        ]


        mutator = mutators[random.randint(0, len(mutators)-1)]

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

# mutator = Mutator()
#
#
# out = mutator.mutate([-41, 2, 1321])
# print(out)
