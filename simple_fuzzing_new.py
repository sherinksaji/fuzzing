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
        self.analyzer = CoAPCoverageMiddleware()

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
        return self.mutator.mutate_str(payload)
    
    def fuzz_resource_path(self):
        # Modify resource paths accessed by the fuzzer
        # Example: Generate random paths or mutate existing paths
        return self.mutator.mutate_arr(self.resource_paths)
    
    def fuzz_method(self):
        # Modify resource paths accessed by the fuzzer
        return self.mutator.mutate_arr(self.method)
    
    def fuzz_message_type(self):
        # Modify the type of CoAP messages sent by the fuzzer
        # Example: Change between CON, NON, ACK, RST
        return self.mutator.mutate_arr(self.msgtypes)
        
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
    
    def isInterestingCoAP(self, path):
        # Get coverage data (assuming you have a method to retrieve coverage data)
        self.isInteresting.append(path)
        # Use isInteresting method from AFL_Fuzzer
        if path not in self.interestingPaths:
            self.interestingPaths.append(path)
            #print("Coverage is interesting!")
            #mutated_input = self.mutate_t(seed_input, 0)
            # self.seedQ.append(mutated_input)
            return True
        return False

    def runTestRevealsCrashOrBug(self, seed_input, response):
        try:
            #print("Running test to reveal crash or bug...")
            message_type = response.type
            if message_type == defines.Types['CON']:
                # Confirmable message type
                if seed_input.method in ['GET', 'POST', 'PUT', 'DELETE']:
                    # Compatible methods for CON messages
                    # Perform test or validation specific to CON messages
                    message_="Performing test for CON message with method:{}".format(seed_input.method)
                    print(message_)
                    with open('error.txt', 'a') as file:
                        file.write(message_ + '\n')
                else:
                    error_message = "Error: Incompatible method '{}' for CON message type.".format(seed_input.method)
                    print(error_message)
                    with open('error.txt', 'a') as file:
                        file.write(error_message + '\n')
            elif message_type == defines.Types['NON']:
                # Non-confirmable message type
                if seed_input.method in ['GET', 'OBSERVE']:
                    # Compatible methods for NON messages
                    # Perform test or validation specific to NON messages
                    message_="Performing test for NON message with method:'{}'".format(seed_input.method)
                    print(message_)
                    with open('error.txt', 'a') as file:
                        file.write(message_ + '\n')
                else:
                    error_message = "Error: Incompatible method '{}' for NON message type.".format(seed_input.method)
                    print("Error: Incompatible method", seed_input.method, "for NON message type.")
                    with open('error.txt', 'a') as file:
                        file.write(error_message + '\n')
            elif message_type == defines.Types['ACK']:
                # Acknowledgement message type
                # Perform actions specific to ACK messages
                message_="Received ACK message."
                print("Received ACK message.")
                with open('error.txt', 'a') as file:
                    file.write(message_ + '\n')
            elif message_type == defines.Types['RST']:
                # Reset message type
                # Perform actions specific to RST messages
                message_="Received RST message."
                print("Received RST message.")
                with open('error.txt', 'a') as file:
                    file.write(message_ + '\n')
        except Exception as e:
            # Print any errors during bug testing
            message_="Error during bug testing:", e
            print(message_)
            with open('error.txt', 'a') as file:
                file.write(message_ + '\n')

    def fuzz_and_send_requests(self, num_requests, num_bytes, token_message_length):
        for _ in range(num_requests):
            # print(_)
            #print("Seed queue length before accessing seed input:", len(self.seedQ))
            seed_input = self.seedQ[0]
            if seed_input is not None:
                E = self.AssignEnergy(seed_input)
                
                for i in range(1,E):
                    random_payload = self.fuzz_payload(self.original_payload)
                    random_header = self.fuzz_header()
                    random_resourcepath = self.fuzz_resource_path()
                    random_type=self.fuzz_message_type()
                    random_method=self.fuzz_method()
                    # Create CoAPInput object with random values
                    t_prime = CoAPInput(random_payload, random_header, random_resourcepath, random_type, random_method) # fuzzed input
                    # Append the CoAPInput object to seedQ
                    # self.seedQ.append(input_object)
                    #seed_input.print_CoAPInput()
                    
                    # fuzzing
                    try:
                        resource_path = t_prime.resourcepath
                        fuzzed_header = t_prime.header
                        fuzzed_payload = t_prime.payload
                        fuzzed_method = t_prime.method
                        fuzzed_msgtype = t_prime.msgtype
                        print("Fuzzing payload:", repr(fuzzed_payload))
                        # print("Fuzzed message type:", fuzzed_msgtype)  # Print fuzzed message type
                        if fuzzed_method == 'GET':
                            response = self.client.get(resource_path, payload=fuzzed_payload, header=fuzzed_header ,msg_type=defines.Types[fuzzed_msgtype])
                        elif fuzzed_method == 'POST':
                            response = self.client.post(resource_path, payload=fuzzed_payload, header=fuzzed_header, msg_type=defines.Types[fuzzed_msgtype])
                        elif fuzzed_method == 'PUT':
                            response = self.client.put(resource_path, payload=fuzzed_payload, header=fuzzed_header,msg_type=defines.Types[fuzzed_msgtype])
                        elif fuzzed_method == 'DELETE':
                            response = self.client.delete(resource_path, payload=fuzzed_payload, header=fuzzed_header,msg_type=defines.Types[fuzzed_msgtype])
                        elif fuzzed_method == 'OBSERVE':
                            response = self.client.observe(resource_path, callback=None, msg_type=defines.Types[fuzzed_msgtype])
                        elif fuzzed_method == 'DISCOVER':
                            response = self.client.discover(callback=None, msg_type=defines.Types[fuzzed_msgtype])
                        print(response.pretty_print())

                        # Check for crash or bug
                        coverage_data = self.analyzer.analyze_coverage()
                        path = self.process_coverage(coverage_data) 

                        for i, tup in enumerate(self.pathCoverage):
                            if path == tup[1]:
                                tup[0].append(t_prime)
                                tup[1] += 1
                                self.pathCoverage[0][1] += 1
                                changed = True
                            if i == len(self.pathCoverage) - 1 and changed != True:
                               self.pathCoverage.append((path, 1))   

                        self.runTestRevealsCrashOrBug(seed_input,response)
                        interesting = self.isInterestingCoAP(seed_input, path)
                        if interesting == True:
                            self.seedQ.append(t_prime)
                        # Remove the first input from seedQ
                        # self.seedQ.pop(0)

                    except Exception as e:
                        # Log the error
                        print("Fuzzing error:", e)
            else:
                    print("Seed input is None")


    def close_connection(self):
        self.client.stop()

def main():
    host = "127.0.0.1"
    port = 5683

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    fuzzer = CoAPFuzzer(host, port)
    #while(1):
    seedQlength=1000
    fuzzer.init_seedQ(seedQlength)

    try:
        number=0
        while fuzzer.seedQ:
            print("Iteration:",number)
            fuzzer.analyzer.start_coverage()
            fuzzer.fuzz_and_send_requests(num_requests=1, num_bytes=5,token_message_length=8)
            #print("Coverage data for input", number, ":")
            #coverage_data_show=fuzzer.analyzer.analyze_coverage()
            #print(coverage_data_show)
            #coverage_data = fuzzer.analyzer.stop_coverage()
            number+=1
            #print("Coverage data for input", number, ":", coverage_data)

    except Exception as e:
        traceback.print_exc()
        logger.error("Fuzzing error: %s", e)

    finally:
        fuzzer.analyzer.stop_coverage()
        fuzzer.close_connection()

if __name__ == "__main__":
    main()
