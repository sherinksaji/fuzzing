from coapthon.client.helperclient import HelperClient
import random
import logging
import coverage
import os
from Mutator import Mutator
from AFL_base import AFL_Fuzzer
import struct

class CoAPFuzzer(AFL_Fuzzer):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = HelperClient(server=(self.host, self.port))
        self.mutator = Mutator()
        self.original_payload = self.generate_random_str(8)
        self.logger = logging.getLogger(__name__)
        AFL_Fuzzer.__init__(self)

    def fuzz_payload(self, payload, num_bytes):
        # Generate random bytes to replace part of the payload
        # fuzz_bytes = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(num_bytes))
        # return payload[:3] + fuzz_bytes + payload[3 + num_bytes:]
        print('Payload:',payload)
        print('Fuzzing Payload Mutator Function:')
        return self.mutate_str(payload)
    
    def fuzz_resource_path(self):
        # Modify resource paths accessed by the fuzzer
        # Example: Generate random paths or mutate existing paths
        resource_paths = ['/basic', '/storage', '/child', '/separate', '/etag', '/', '/big', '/encoding', '/advancedSeparate', '/void', '/advanced', '/long', '/xml']
        return random.choice(resource_paths)
    
    def fuzz_message_type(self):
        # Modify the type of CoAP messages sent by the fuzzer
        # Example: Change between CON, NON, ACK, RST
        message_types = ["CON", "NON", "ACK", "RST"]
        return random.choice(message_types)
        
    def fuzz_header(self, token_message_length):
        # Generate fuzzed CoAP header
        version = random.randint(1, 2)
        types = {'CON': 0, 'NON': 1, 'ACK': 2, 'RST': 3}
        type_ = self.fuzz_message_type()
        token_length = random.randint(0, 8)  # Maximum token length in CoAP is 8 bytes
        token = self.generate_random_str(token_length)
        # Generate a long string for the token message
        #token_message =self.generate_random_str(token_message_length) #'A' * token_message_length
        #print('Token Message:',token_message)
        #print('Fuzzing Token Message Mutator Function:')
        #fuzzed_token_message = self.mutate_str(token_message)
        code = random.randint(0, 255)  # CoAP code is an 8-bit value
        message_id = random.randint(0, 65535)  # Message ID is a 16-bit value
        # Pack the header fields into bytes 
        header_bytes = struct.pack('!BBBH', (version << 6) | (token_length & 0x0F), types[type_], code, message_id)
        header_bytes += token.encode('utf-8')
        #header_bytes += fuzzed_token_message.encode('utf-8')  # Append the token message to the header
        return header_bytes

    def fuzz_and_send_requests(self, num_requests, num_bytes,token_message_length):
        for _ in range(num_requests):
            #print(_)
            resource_path = self.fuzz_resource_path()
            fuzzed_header = self.fuzz_header(token_message_length)
            fuzzed_payload = self.fuzz_payload(self.original_payload, num_bytes)
            print("Fuzzing payload:", repr(fuzzed_payload))

            # Send fuzzed GET request with the fuzzed payload and path "/basic/"
            # response = self.client.get("/basic",payload=fuzzed_payload, header=fuzzed_header)
            response = self.client.get(resource_path,payload=fuzzed_payload, header=fuzzed_header)
            print(response.pretty_print())


    def close_connection(self):
        self.client.stop()

def main():
    host = "127.0.0.1"
    port = 5683

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()

    fuzzer = CoAPFuzzer(host, port)
    #while(1):
    fuzzed= 20
    try:
        for i in range (fuzzed):
            print(i)
            fuzzer.fuzz_and_send_requests(num_requests=1, num_bytes=5,token_message_length=8)
    except Exception as e:
        logger.error("Fuzzing error: %s", e)
    finally:
        # Close connection and stop coverage measurement
        fuzzer.close_connection()
        cov.stop()
        cov.save()
        cov.report()
        #cov.report(show_missing=True)
        #Get coverage data
        cov_data = cov.get_data()

        # Extract covered lines for each file
        covered_lines_per_file = {}
        for filename in cov_data.measured_files():
            basename = os.path.basename(filename)
            covered_lines_per_file[basename] = [lineno for lineno in cov_data.lines(filename) if lineno != 0]
        #print(covered_lines_per_file)
        logger.debug("Covered lines per file: %s", covered_lines_per_file)

if __name__ == "__main__":
    main()
