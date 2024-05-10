from mutator import Mutator
import random


def read_t_prime():
    with open("t_prime.txt", "r") as file:
        hex_string = file.read().strip()  # Strip any leading/trailing whitespace
    byte_values = [int(hex_string[i : i + 2], 16) for i in range(0, len(hex_string), 2)]
    return byte_values


def bytes_to_hex_string(byte_list):
    return "".join([format(b, "02x") for b in byte_list])


def write_t_prime(bytes_list):
    hex_string = bytes_to_hex_string(bytes_list)
    with open("t_prime.txt", "w") as file:
        file.write(hex_string)


write_t_prime([0x01, 0x02])

t_prime = read_t_prime()
print([0x01, 0x02])

print("t_prime : ", t_prime)

mutator = Mutator()


new_t_prime = mutator.mutate_byte_list(t_prime)

print("new_t_prime : ", new_t_prime)


def write_result(t_prime, bug=False):
    crash = False
    zephyr_died = random.choice([True, False])
    if zephyr_died:
        crash = True
    with open("result.txt", "a") as file:
        file.write("t_prime : " + str(t_prime) + "\n")
        if crash:
            file.write("Resulted in crash. \n")
        elif bug:
            file.write("Resulted in bug. \n")


write_result([0x01])
write_result([0x02, 0x03])
