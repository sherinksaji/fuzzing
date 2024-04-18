from coapthon.client.helperclient import HelperClient
import random
import logging
from Mutator import Mutator
from AFL_base import AFL_Fuzzer
from CoAPInput import CoAPInput
from CoAPCoverageMiddleware import CoAPCoverageMiddleware
import struct
from coapthon.messages.request import Request
from coapthon import defines
import traceback

class CoAPFuzzer(AFL_Fuzzer):
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = HelperClient(server=(self.host, self.port))
        self.mutator = Mutator()
        self.original_payload = self.generate_random_str(8)
        self.logger = logging.getLogger(__name__)
        AFL_Fuzzer.__init__(self)
        self.resource_paths=['/basic', '/storage', '/child', '/separate', '/etag', '/', '/big', '/encoding', '/advancedSeparate', '/void', '/advanced', '/long', '/xml']
        self.msgtypes=["CON", "NON", "ACK", "RST"]
        self.method=['GET', 'POST', 'PUT', 'DELETE','OBSERVE','DISCOVER']
        self.functions=[self.fuzz_payload,
                        self.fuzz_header,
                        self.fuzz_resource_path,
                        self.fuzz_message_type,
                        self.fuzz_method]
        self.seedQ = []

    def init_seedQ(self,seedQlen):
        for i in range(seedQlen):
            random_payload = self.fuzz_payload(self.original_payload)
            random_header = self.fuzz_header()
            random_resourcepath = self.fuzz_resource_path()
            random_type=self.fuzz_message_type()
            random_method=self.fuzz_method()
            # Create CoAPInput object with random values
            input_object = CoAPInput(random_payload, random_header, random_resourcepath, random_type, random_method)
            # Append the CoAPInput object to seedQ
            self.seedQ.append(input_object)

    def fuzz_payload(self,payload):
        # Generate random bytes to replace part of the payload
        # fuzz_bytes = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(num_bytes))
        # return payload[:3] + fuzz_bytes + payload[3 + num_bytes:]
        return self.mutate_str(payload)
    
    def fuzz_resource_path(self):
        # Modify resource paths accessed by the fuzzer
        # Example: Generate random paths or mutate existing paths
        return random.choice(self.resource_paths)
    
    def fuzz_method(self):
        # Modify resource paths accessed by the fuzzer
        return random.choice(self.method)
    
    def fuzz_message_type(self):
        # Modify the type of CoAP messages sent by the fuzzer
        # Example: Change between CON, NON, ACK, RST
        return random.choice(self.msgtypes)
    
    def mutate_t(self, t, index):
        t.payload=self.fuzz_payload(t.payload)
        t.header=self.fuzz_header()
        t.resourcepath=self.fuzz_resource_path()
        t.method=self.fuzz_method()
        t.msgtype=self.fuzz_message_type()
        
    def fuzz_header(self):
        # Generate fuzzed CoAP header
        version = random.randint(1, 2)
        types = {'CON': 0, 'NON': 1, 'ACK': 2, 'RST': 3}
        type_ = self.fuzz_message_type()
        token_length = random.randint(0, 8)  # Maximum token length in CoAP is 8 bytes
        token = self.generate_random_str(token_length)
        code = random.randint(0, 255)  # CoAP code is an 8-bit value
        message_id = random.randint(0, 65535)  # Message ID is a 16-bit value
        # Pack the header fields into bytes 
        header_bytes = struct.pack('!BBBH', (version << 6) | (token_length & 0x0F), types[type_], code, message_id)
        header_bytes += token.encode('utf-8')
        return header_bytes


    def fuzz_and_send_requests(self, num_requests, num_bytes, token_message_length):
        for _ in range(num_requests):
            # print(_)
            print("Seed queue length before accessing seed input:", len(self.seedQ))
            seed_input = self.seedQ[0]
            seed_input.print_CoAPInput()
            if seed_input is not None:  # Check if seed_input is not None
                try:
                    resource_path = seed_input.resourcepath
                    fuzzed_header = seed_input.header
                    fuzzed_payload = seed_input.payload
                    fuzzed_method = seed_input.method
                    fuzzed_msgtype = seed_input.msgtype
                    print("Fuzzing payload:", repr(fuzzed_payload))
                    print("Fuzzed message type:", fuzzed_msgtype)  # Print fuzzed message type
                    if fuzzed_method == 'GET':
                        response = self.client.get(resource_path, payload=fuzzed_payload, header=fuzzed_header)
                    elif fuzzed_method == 'POST':
                        response = self.client.post(resource_path, payload=fuzzed_payload, header=fuzzed_header)
                    elif fuzzed_method == 'PUT':
                        response = self.client.put(resource_path, payload=fuzzed_payload, header=fuzzed_header)
                    elif fuzzed_method == 'DELETE':
                        response = self.client.delete(resource_path, payload=fuzzed_payload, header=fuzzed_header)
                    elif fuzzed_method == 'OBSERVE':
                        response = self.client.observe(resource_path, callback=None)
                    elif fuzzed_method == 'DISCOVER':
                        response = self.client.discover(callback=None)
                    print(response.pretty_print())

                    # Further mutate the input and add to seedQ
                    mutated_input = self.mutate_t(seed_input, 0)
                    self.seedQ.append(mutated_input)
                    # Remove the first input from seedQ
                    self.seedQ.pop(0)

                except Exception as e:
                    # Log the error
                    print("Fuzzing error:", e)
            else:
                print("Seed input is None")

        # Send fuzzed GET request with the fuzzed payload and path "/basic/"
        # response = self.client.get("/basic",payload=fuzzed_payload, header=fuzzed_header)
        # response = self.client.fuzzed_method(resource_path,payload=fuzzed_payload, header=fuzzed_header)
        # print(response.pretty_print())

                # Send fuzzed GET request with the fuzzed payload and path "/basic/"
                # response = self.client.get("/basic",payload=fuzzed_payload, header=fuzzed_header)
                # response = self.client.fuzzed_method(resource_path,payload=fuzzed_payload, header=fuzzed_header)
                # print(response.pretty_print()) 


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
    analyzer=CoAPCoverageMiddleware()
    #while(1):
    seedQlength= 100
    fuzzer.init_seedQ(seedQlength)

    try:
        for i in range (seedQlength):
            print(i)
            fuzzer.fuzz_and_send_requests(num_requests=1, num_bytes=5,token_message_length=8)
    except Exception as e:
        logger.error("Fuzzing error: %s", e)
    finally:
        # Stop coverage measurement
        analyzer.stop_coverage()
        # Optionally, analyze coverage data for further processing with line count
        coverage_data = analyzer.analyze_coverage()
        print("Coverage data:", coverage_data)
        # Close connection and stop coverage measurement
        fuzzer.close_connection()

if __name__ == "__main__":
    main()

