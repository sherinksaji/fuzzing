from fuzzingbook.GreyBoxFuzzer import GreyboxFuzzer


def fuzz_input():
    fuzzer = GreyboxFuzzer()  # Initialize with appropriate configuration
    random_name = (
        fuzzer.fuzz()
    )  # Adapt this part based on how GreyboxFuzzer generates data
    random_info = (
        fuzzer.fuzz()
    )  # Adapt this part based on how GreyboxFuzzer generates data
    random_price = str(
        fuzzer.fuzz()
    )  # Adapt this part based on how GreyboxFuzzer generates data
    return {"name": random_name, "info": random_info, "price": random_price}


# Use the fuzz_input function to generate form_data
form_data = fuzz_input()
