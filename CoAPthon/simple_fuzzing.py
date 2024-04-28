from coapthon.client.helperclient import HelperClient
import random
import string
import logging
import coverage
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CoAPFuzzer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = HelperClient(server=(self.host, self.port))
        self.original_payload = "Hello, CoAP!"

    def fuzz_payload(self, payload, num_bytes):
        # Generate random bytes to replace part of the payload
        fuzz_bytes = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(num_bytes)
        )
        return payload[:3] + fuzz_bytes + payload[3 + num_bytes :]

    def fuzz_and_send_requests(self, num_requests, num_bytes):
        for _ in range(num_requests):
            fuzzed_payload = self.fuzz_payload(self.original_payload, num_bytes)
            print("Fuzzing payload:", fuzzed_payload)

            # Send fuzzed GET request with the fuzzed payload and path "/basic/"
            response = self.client.get("/basic", payload=fuzzed_payload)
            print(response.pretty_print())

    def close_connection(self):
        self.client.stop()


def main():
    host = "127.0.0.1"
    port = 5683

    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()

    fuzzer = CoAPFuzzer(host, port)
    # while(1):
    #    try:
    fuzzer.fuzz_and_send_requests(num_requests=3, num_bytes=5)
    #    except:
    fuzzer.close_connection()

    cov.stop()
    cov.save()
    cov.report()
    # cov.report(show_missing=True)

    # Get coverage data
    # cov_data = cov.get_data()

    # # Extract covered lines for each file
    # covered_lines_per_file = {}
    # for filename in cov_data.measured_files():
    #     basename = os.path.basename(filename)
    #     covered_lines_per_file[basename] = [lineno for lineno in cov_data.lines(filename) if lineno != 0]

    # Print covered lines for each file
    # for filename, covered_lines in covered_lines_per_file.items():
    #     print("File:", filename)
    #     print("Covered lines:", covered_lines)
    print(covered_lines_per_file)


if __name__ == "__main__":
    main()
