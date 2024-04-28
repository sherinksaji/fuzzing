import requests
import random
import json
import coverage
import os
import subprocess
import time
import string
from djangoInput import DjangoInput

from AFL_base import AFL_Fuzzer
import subprocess
import random
from djangoInput import DjangoInput


class DjangoFuzzer(AFL_Fuzzer):

    def __init__(self):
        super().__init__()
        self.init_seedQ()
        # print("init>first t : ", self.seedQ[0][0])

    def init_seedQ(self):

        random_name = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)
        )
        random_info = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)
        )
        random_price = str(random.randint(1, 100))

        self.seedQ[0] = (
            DjangoInput(random_name, random_info, random_price),
            None,
        )
        # print("init_seedQ first t : ", self.seedQ[0][0])

    def generate_fuzzed_token(self, length=32):
        """
        Generate a fuzzed token for use as a csrftoken or sessionid.
        Generates a random hexadecimal string of the specified length.

        Parameters:
        length (int): The length of the token to generate. Default is 32.

        Returns:
        str: A string representing the fuzzed token.
        """
        # Hexadecimal characters only include 0-9 and a-f.
        hex_chars = string.digits + "abcdef"
        # Generate a random string of the specified length from the hex_chars.
        token = "".join(random.choice(hex_chars) for _ in range(length))
        return token

    def mutate_t(self, t, index):
        # print("mutate_t in sendRequest.py was called")
        # mutate however u want --> u do not neccessarily have to use the index
        # but please don't remove index as an argument to the function
        if index == 0:
            t.name = self.mutate_str(t.name)

        elif index == 1:
            t.info = self.mutate_str(t.info)

        elif index == 2:
            t.price = str(random.randint(1, 100))

        elif index == 3:
            t.csrftoken = self.generate_fuzzed_token(32)

        elif index == 4:
            t.sessionid = self.generate_fuzzed_token(32)

        # print("DjangoFuzzer>mutate_t>", t)
        return t

    def send_request(self, form_data, headers):
        base_url = "http://127.0.0.1:8000/datatb/product/"

        endpoint_url = "add/"

        url = base_url + endpoint_url

        try:
            print(json.dumps(form_data))
            response = requests.post(url, headers=headers, data=json.dumps(form_data))

            if response.status_code == 200:
                print("Request successful!")
                print("Response:")
                print(response.text)

            else:
                print(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)

        return response.status_code != 200

    # ping

    def runTestRevealsCrashOrBug(self, t_prime):
        # print("t_prim in run : ", t_prime)
        django_process = subprocess.Popen(
            ["coverage", "run", "--branch", "manage.py", "runserver"]
        )
        time.sleep(10)
        numberOfRequests = 1
        for i in range(numberOfRequests):
            revealsCrashOrBug = self.send_request(
                t_prime.getFormData(), t_prime.getHeader()
            )
        # time.sleep(60)
        django_process.terminate()
        django_process.wait()

        subprocess.run(["coverage", "json"])
        subprocess.run(["coverage", "lcov"])

        with open("coverage.json", "r") as f:
            coverage_data = json.load(f)

        return revealsCrashOrBug, coverage_data


djangoFuzzer = DjangoFuzzer()
djangoFuzzer.fuzz()
