import string
import random
from mutator import Mutator



class Fuzzer:
    def __init__(self, initial_input):
        self.seedQ = [initial_input]
        self.failureQ = []
        self.mutator = Mutator()
        self.path_coverage = []

    def is_interesting(self, path, input):
        if path not in self.path_coverage:
            self.path_coverage.append(path)
            self.seedQ.append(input)
            return True

        return False

    def chooseNext(self):
        nextSeed = self.seedQ[0]
        self.seedQ = self.seedQ[1:]
        return nextSeed

    def assignEnergy(self):
        return 500

    def mutate(self, attri):
        return self.mutator.mutate(attri)





    def execute_fuzzing(self):
        pass



