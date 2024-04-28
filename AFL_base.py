from copy import deepcopy
from mutator import Mutator
import hashlib
from abc import ABC, abstractmethod


# copy this file into which ever directory u want to use yr child fuzzer in
# u probably want to use your child fuzzer within the directory of the target u are fuzzing
class AFL_Fuzzer(ABC):
    def __init__(self, ):
        seedQ = []
        self.seedQ = seedQ
        self.failureQ = []
        self.pathCoverage = []
        self.pathCoverage.append(('totalPaths', 0))
        self.interestingPaths = []
        self.mutator = Mutator()
        self.numberOfTimes = 1

    @abstractmethod
    def init_seedQ(self):
        # add first input to seedQ
        pass

    def ChooseNext(self):
        # insert function

        # Handle the case when seedQ is empty #seedQ will not be empty for ChooseNext
        # if not self.seedQ:
        #     return None
        # # Find the input t with the maximum path coverage#consider changing to max line coverage?
        # next_input = max(self.seedQ, key=self.seedQ.get, default=None)

        # next_input = self.seedQ[0]

        # # Remove the extracted input from seedQ
        # del self.seedQ[next_input]
        # # Return the chosen input t
        next_input = self.seedQ.pop(0)[0]
        # print("ChooseNext : ", next_input)
        return next_input

    def AssignEnergy(self, t):
        for i in self.pathCoverage:
            if isinstance(i[1], list) and t in i[1]:
                if self.pathCoverage[0][1] == 0:
                    return 512
                return 512 * self.numberOfTimes * (1 - (i[2] / self.pathCoverage[0][1]))
        
    def get_bucket_index(self, taken):
        bucket_index = -1
        buckets = {
            "A": {"start": 1, "end": 1},
            "B": {"start": 2, "end": 2},
            "C": {"start": 3, "end": 3},
            "D": {"start": 4, "end": 7},
            "E": {"start": 8, "end": 15},
            "F": {"start": 16, "end": 31},
            "G": {"start": 32, "end": 127},
            "H": {"start": 128, "end": float("inf")},
        }

        for key in buckets:
            if taken >= buckets[key]["start"] and taken <= buckets[key]["end"]:
                bucket_index = key
        return bucket_index

    def process_coverage(self, coverage):
        branches = []
        path_len = 0
        for key in coverage:
            branch_str = (
                key[0] + "_" + str(key[1]) + "_" + self.get_bucket_index(coverage[key]) 
            )
            branches.append(branch_str)
            path_len += 1
        branches.sort()
        # print("".join(branches))
        hash_object = hashlib.md5(",".join(branches).encode())
        short_string = hash_object.hexdigest()

        return short_string

    def isInteresting(self, path):
        # path = self.process_coverage(coverage)
        if path not in self.interestingPaths:
            self.interestingPaths.append(path)
            print("t is interesting")
            return True
        print("t is not interesting")
        return False

    # def mutate_default_data_type(self, input):
    #     # insert function
    #     mutator = Mutator()
    #     # probabilities to be determined after pilot fuzzing, these are just test values set
    #     mutator_probabilities = [0.1, 0.1, 0.2, 0.2, 0.2, 0.1, 0.1]
    #     selected_mutator = random.choices(
    #         mutator.mutators, weights=mutator_probabilities
    #     )[0]
    #     mutated_input = selected_mutator(input)
    #     return mutated_input

    @abstractmethod
    def mutate_t(self, t):
        # t is an object
        print("mutate_t in AFL_base.py was called")
        pass

    @abstractmethod
    def runTestRevealsCrashOrBug(self, t_prime):
        # return crashOrBug, t_prime_executed_lines
        pass

    async def fuzz(self):
        while len(self.seedQ) >= 1:  # and timeout?
            t = self.ChooseNext()
            E = self.AssignEnergy(t)
            for i in range(1, E):
                t_prime = self.mutate_t(t)
                crashOrBug, t_prime_coverage_data, covered_lines = (
                    await self.runTestRevealsCrashOrBug(t_prime)
                )
                path = self.process_coverage(t_prime_coverage_data)
                if crashOrBug:
                    print("adding t to failureQ")
                    self.failureQ.append(t_prime)
                    for i, tup in enumerate(self.pathCoverage):
                        if path == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] += 1
                            self.pathCoverage[0][1] += 1
                            changed = True
                        if i == len(self.pathCoverage) - 1 and changed != True:
                            self.pathCoverage.append((path, 1))
                elif self.isInteresting(path) == True:
                    print("adding t to seedQ")
                    self.seedQ.append((t_prime, path, covered_lines))
                    for i, tup in enumerate(self.pathCoverage):
                        if path == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] += 1
                            self.pathCoverage[0][1] += 1
                            changed = True
                        if i == len(self.pathCoverage) - 1 and changed != True:
                            self.pathCoverage.append((path, 1))
            self.numberOfTimes += 1

# def Main():
#     while SeedQ[0] != None: # and timeout?
#         t = ChooseNext(SeedQ)
#         E = AssignEnergy(t)
#         for i in range (1, E):
#             t_prime = MutateInput(t)
#             if t_prime == 1:
#                 FailureQ.append(t_prime)
#             elif isInteresting(t_prime) == True:
#                 SeedQ.append(t_prime)


def printDict(dictName, dict):
    print("printing " + dictName + "...")
    for k, v in dict.items():
        print("key = {} : value = {}".format(k, v))