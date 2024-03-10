from boofuzz import *
import random
import json


# class CustomMutation(Mutation):
#     def mutate_string(self, data):
#         # Implement your custom mutation logic here
#         # This method should return the mutated data
#         return "".join(
#             random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)
#         )

#     def mutate_double(self, data):
#         return str(round(random.uniform(1.0, 100.0), 2))

#     def mutate_int(self, data):
#         return random.int(1, 100)


# class CustomFuzzer(FuzzLoggerBase):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.seed_queue = ["SeedQ"]
#         self.failure_queue = []

#     def choose_next(self):
#         return self.seed_queue.pop(0)

#     def assign_energy(self, testcase):
#         # Implement energy assignment logic here
#         return 1  # For simplicity, always return 1

#     def mutate_input(self, testcase):
#         mutator = CustomMutation()
#         return mutator.mutate(testcase)

#     def is_interesting(self, testcase):
#         # Implement interestingness check logic here
#         return False

#     def fuzz(self):
#         while self.seed_queue:
#             t = self.choose_next()
#             energy = self.assign_energy(t)
#             for i in range(energy):
#                 t_prime = self.mutate_input(t)
#                 if self.reveals_bug(t_prime):
#                     self.failure_queue.append(t_prime)
#                 elif self.is_interesting(t_prime):
#                     self.seed_queue.append(t_prime)

#     def reveals_bug(self, testcase):
#         # Implement bug/crash detection logic here
#         return False

#     def pre_send(self, connection, testcase):
#         # Implement preprocessing logic here
#         pass

#     def post_send(self, connection, testcase):
#         # Implement post-send logic here
#         pass

#     def post_testcase(self, connection, testcase):
#         # Implement post-testcase logic here
#         pass


from boofuzz import *
import random


# def generate_random_json():
#     random_name = "".join(
#         random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)
#     )
#     random_info = "abcd"
#     random_price = str(random.randint(1, 100))
#     return {"name": random_name, "info": random_info, "price": random_price}


# # Define the target
# target = Target(connection=SocketConnection("127.0.0.1", 8000, proto="tcp"))

# # Define the session
# session = Session(target=target)

# s_initialize(name="Fuzz POST Request")
# with s_block("Request-Line"):
#     s_string("POST", fuzzable=False)
#     s_delim(" ", fuzzable=False)
#     s_string("/datatb/product/add/", fuzzable=False)
#     s_delim(" ", fuzzable=False)
#     s_string("HTTP/1.1", fuzzable=False)
#     s_static("\r\n", name="Request-Line-CRLF")
#     s_string("Host:", fuzzable=False)
#     s_delim(" ", fuzzable=False)
#     s_string("127.0.0.1:8000", fuzzable=False)
#     s_static("\r\n", name="Host-CRLF")
#     s_string("Content-Type:", fuzzable=False)
#     s_delim(" ", fuzzable=False)
#     s_string("application/json", fuzzable=False)
#     s_static("\r\n", name="Content-Type-CRLF")
#     s_static("\r\n", name="Header-CRLF")

#     json_data = generate_random_json()
#     json_string = json.dumps(json_data)
#     s_static(json_string, name="json-payload")
# session.connect(s_get("Fuzz POST Request"))
# for i in range(1000):
#     session.fuzz()
# Define the target
target = Target(connection=SocketConnection("127.0.0.1", 8000, proto="tcp"))

# Define the session
session = Session(target=target)

price = str(
    random.uniform(1.0, 100.0)
)  # Generate a floating-point number as an example


s_initialize(name="Fuzz POST Request")
with s_block("Request-Line"):
    s_string("POST", fuzzable=False)
    s_delim(" ", fuzzable=False)
    s_string("/datatb/product/add/", fuzzable=False)
    s_delim(" ", fuzzable=False)
    s_string("HTTP/1.1", fuzzable=False)
    s_static("\r\n", name="Request-Line-CRLF")
    s_string("Host:", fuzzable=False)
    s_delim(" ", fuzzable=False)
    s_string("127.0.0.1:8000", fuzzable=False)
    s_static("\r\n", name="Host-CRLF")
    # Add more headers as needed, e.g., Content-Type
    s_string("Content-Type:", fuzzable=False)
    s_delim(" ", fuzzable=False)
    s_string("application/json", fuzzable=False)
    s_static("\r\n", name="Content-Type-CRLF")
    s_static("\r\n", name="Header-CRLF")

    random_name = "".join(
        random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)
    )
    random_info = "abcd"
    random_price = str(round(random.randint(1, 100), 2))

    # JSON payload starts here
    s_static("{", name="json-start")
    s_static('"name": "', name="json-name-label")
    s_string(random_name, name="json-name-value")
    s_static('", "info": "', name="json-info-label")
    s_static(random_info, name="json-info-value")
    s_static('", "price": ', name="json-price-label")
    s_static(random_price, name="json-price-value")
    s_static("}", name="json-end")

session.connect(s_get("Fuzz POST Request"))
session.fuzz()
