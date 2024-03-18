import string
import random
from mutator import Mutator



class Fuzzer:
    def __init__(self, len_limit,):
      self.len_limit = len_limit
      self.seedQ = []
      self.failureQ = []
      self.mutator = Mutator()


    def generate_random_str(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        result_str = ''.join(random.choice(characters) for _ in range(self.len_limit))
        self.seedQ.append(result_str)
                
        return result_str
    
    def mutate_str(self, input):
        return self.mutator.mutate_str(input_str=input)


    def execute_fuzzing(self):
        pass



