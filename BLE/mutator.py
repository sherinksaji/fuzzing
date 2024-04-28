import random
import time

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
        self.prev_output = None

    def __init__(self) -> None:
        pass

    def bit_flip(self, byte):
        return byte ^ random.choice(FLIP_ARRAY)

    def magic(self, data, idx):
        picked_magic = random.choice(MAGIC_VALS)

        offset = 0
        for m in picked_magic:
            data[idx + offset] = m
            offset += 1

    def mutate_number(self, original_number, turnOffSmallAndBig=False):

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

        if turnOffSmallAndBig:
            print("turned off")
            mutators = [
                add_subtract_random_value,
                multiply_divide_random_factor,
                flip_random_bit,
            ]

        else:
            print("not turned off")
            mutators = [
                add_subtract_random_value,
                multiply_divide_random_factor,
                flip_random_bit,
                generate_large_number,
                generate_small_number,
            ]

        mutator = mutators[random.randint(0, len(mutators) - 1)]

        return mutator(original_number)

    def mutate_bytestring(self, bs, mutators_usable=[1, 2, 3, 4, 5, 6]):

        def replace_random_byte(bs):

            if bs:
                ba = bytearray(bs)
                index = random.randint(0, len(ba) - 1)
                ba[index] = random.randint(0, 255)
                return bytes(ba)
            return bs

        def add_random_byte(bs):

            ba = bytearray(bs)
            index = random.randint(0, len(ba))
            ba.insert(index, random.randint(0, 255))
            return bytes(ba)

        def remove_random_byte(bs):

            if bs:
                ba = bytearray(bs)
                index = random.randint(0, len(ba) - 1)
                del ba[index]
                return bytes(ba)
            return bs

        def flip_random_bit(bs):

            if bs:
                ba = bytearray(bs)
                num_bits_to_flip = random.randint(1, len(ba) * 8)
                byte_index = random.randint(0, len(ba) - 1)
                for i in range(num_bits_to_flip):
                    bit_position = random.randint(0, 7)
                    ba[byte_index] ^= 1 << bit_position
                return bytes(ba)
            return bs

        def havoc(bs):
            ba = bytearray(bs)
            ba.insert(0, 255)
            return bytes(ba)

        def append_random_bytes(bs):

            ba = bytearray(bs)
            num_bytes = random.randint(1, 10)
            ba.extend(random.randint(0, 255) for _ in range(num_bytes))
            return bytes(ba)

        # List of mutators

        mutators = [
            replace_random_byte,
            add_random_byte,
            remove_random_byte,
            flip_random_bit,
            havoc,
            append_random_bytes,
        ]

        # Select a random mutator and apply it
        mutator = random.choice(mutators)
        return mutator(bs)

    def mutate_bytearray(self, ba):

        def replace_random_byte(ba):

            if ba:
                index = random.randint(0, len(ba) - 1)
                ba[index] = random.randint(0, 255)
            return ba

        def add_random_byte(ba):

            index = random.randint(0, len(ba))
            ba.insert(index, random.randint(0, 255))
            return ba

        def remove_random_byte(ba):

            if ba:
                index = random.randint(0, len(ba) - 1)
                del ba[index]
            return ba

        def flip_random_bit(ba):

            if not ba:
                return ba
            num_bits_to_flip = random.randint(1, len(ba) * 8)
            byte_index = random.randint(0, len(ba) - 1)
            for i in range(num_bits_to_flip):
                bit_position = random.randint(0, 7)
                ba[byte_index] ^= 1 << bit_position

            return ba

        def havoc(ba):
            if ba:
                ba.insert(0, 255)
            return ba

        def extend_with_random_bytes(ba):

            num_bytes = random.randint(1, 10)
            ba.extend(random.randint(0, 255) for _ in range(num_bytes))
            return ba

        # List of mutators
        mutators = [
            replace_random_byte,
            add_random_byte,
            remove_random_byte,
            flip_random_bit,
            havoc,
            extend_with_random_bytes,
        ]

        # Select a random mutator and apply it
        mutator = random.choice(mutators)
        return mutator(ba)

    def mutate_byte_list(self, byte_list, usable_mutators=[0, 1, 2, 3, 4, 5, 6, 7]):
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
        mutators = []
        for i in usable_mutators:
            if i == 0:
                mutators.append(insert1)
            elif i == 1:
                mutators.append(insert0)
            elif i == 2:
                mutators.append(replace_random_byte)
            elif i == 3:
                mutators.append(add_random_byte)
            elif i == 4:
                mutators.append(remove_random_bytes)
            elif i == 5:
                mutators.append(flip_random_bit)
            elif i == 6:
                mutators.append(havoc)
            elif i == 7:
                mutators.append(extend_with_random_bytes)

        print(mutators)

        mutator = random.choices(mutators)[0]
        # print(mutator)
        # probability = random.random()
        # if probability < 0.1:
        #     return empty()
        return mutator(byte_list)


# Test
mutator = Mutator()
byte_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
print(byte_list)
mutated = mutator.mutate_byte_list(byte_list, [7])
print(mutated)


# byte_string = bytes([65, 66, 67, 68, 69])
# print(byte_string)
# bs = mutator.mutate_bytestring(byte_string)
# print(bs)

# byte_array = bytearray([65, 66, 67, 68, 69])
# print(byte_array)
# ba = mutator.mutate_bytearray(byte_array)
# print(ba)
