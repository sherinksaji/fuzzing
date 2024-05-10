import random
import math


def mutate_length(data, max_length=40):
    if random.choice([True, False]):  # Randomly decide to increase or decrease length
        # Decrease length
        print("Decrease Length")
        new_length = random.randint(0, len(data))
        print("new_length : ", new_length)
        return data[:new_length]
    else:
        # Increase length
        print("Increase Length")
        new_length = random.randint(len(data), max_length)
        print("new_length : ", new_length)
        addedData = [random.randint(0, 300) for _ in range(new_length - len(data))]
        print("padding : ", addedData)
        return data + addedData


# print("after mutated length : ", mutate_length([1, 2, 3, 4]))


def mutate_content(data):

    print("mutated_data : ", data)
    if len(data) < 10:
        mutateDivisor = 2  # Mutate up to 1/2 of the array
    else:
        mutateDivisor = 4  # Mutate up to 1/4 of the array
    num_mutations = random.randint(1, max(1, len(data) // mutateDivisor))

    print("num_mutations", num_mutations)
    for _ in range(num_mutations):
        index = random.randint(0, len(data) - 1)
        print(index)
        data[index] = random.randint(0, 255)

    return data


data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# print("mutate_content", mutate_content(data))


def scramble_data(data):
    data_list = list(data)
    random.shuffle(data_list)
    return data_list


def advanced_mutate(data):
    # Step 1: Mutate Length
    mutated_data = mutate_length(data, max_length=50)

    # Step 2: Mutate Content
    mutated_data = mutate_content(mutated_data)

    # Step 3: Optionally scramble data
    if random.choice([True, False]):
        mutated_data = scramble_data(mutated_data)

    return mutated_data


print("a".encode("utf-8"))

print(b"a" * 10)

number = 1
bytes_needed = math.ceil(math.log2(number + 1) / 8)

print(number.bytes_needed, "big")
