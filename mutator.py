import random

FLIP_RATIO = 0.1 # 1% ratio of bit flips
FLIP_ARRAY = [1, 2, 4, 8, 16, 32, 64, 128]

MAGIC_VALS = [
  [0xFF],
  [0x7F],
  [0x00],
  [0xFF, 0xFF], # 0xFFFF
  [0x00, 0x00], # 0x0000
  [0xFF, 0xFF, 0xFF, 0xFF], # 0xFFFFFFFF
  [0x00, 0x00, 0x00, 0x00], # 0x80000000
  [0x00, 0x00, 0x00, 0x80], # 0x80000000
  [0x00, 0x00, 0x00, 0x40], # 0x40000000
  [0xFF, 0xFF, 0xFF, 0x7F], # 0x7FFFFFFF
]


class Mutator():
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

    def mutate_str(self, input_str):
        data = list(input_str.encode('utf-16'))
        # for byte in data:
        #     print(byte, end=' ')
        # print("\n")

        flips = int(len(data) * FLIP_RATIO)
        flip_indexes = random.choices(range(0, len(data)-6), k=flips)
        # print(flips, flip_indexes)

        methods = [0,1]

        for idx in flip_indexes:
            method = random.choice(methods)

            if method == 0:
                data[idx] = self.bit_flip(data[idx])
            else:
                self.magic(data, idx)

        # for byte in data:
        #     print(byte, end=' ')
        # print("\n")

        print(bytearray(data).decode('utf-16'), '\n\n')


        return bytearray(data).decode('utf-16')