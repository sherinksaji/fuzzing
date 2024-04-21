from copy import deepcopy
import string
import random
from mutator import Mutator
import hashlib
import random
from abc import ABC, abstractmethod


# copy this file into which ever directory u want to use yr child fuzzer in
# u probably want to use your child fuzzer within the directory of the target u are fuzzing
class AFL_Fuzzer(ABC):
    def __init__(self, seedQ):
        self.seedQ = seedQ
        self.failureQ = []
        self.pathCoverage = []
        self.interestingPaths = []
        self.mutator = Mutator()
        self.numberOfTimes = 1

    def ChooseNext(self):
        # Check if seedQ is not empty

        if not self.seedQ:
            return None  # Return None if the list is empty
        if len(self.seedQ) == 1:
            return self.seedQ.pop(0)[0]
        # Initialize the index and the maximum number of covered lines
        max_index = 0
        max_covered_lines = self.seedQ[0][2]

        # Loop through the list to find the tuple with the highest number of covered_lines
        for index, (_, _, covered_lines) in enumerate(self.seedQ):
            if covered_lines > max_covered_lines:
                max_covered_lines = covered_lines
                max_index = index

        # Remove and return the element with the highest covered_lines
        return self.seedQ.pop(max_index)[0]

    def AssignEnergy(self, t):
        for i in self.pathCoverage:
            if isinstance(i[1], list) and t in i[1]:
                return 512 * (1 - (i[2] / self.pathCoverage[0][1]))
        return 512

    @abstractmethod
    def mutate_t(self, t):
        # t is an object
        print("mutate_t in AFL_base.py was called")
        pass

    @abstractmethod
    async def runTestRevealsCrashOrBug(self, t_prime):
        # return crashOrBug, t_prime_executed_lines
        pass

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

    def isInteresting(self, coverage):
        path = self.process_coverage(coverage)
        if path not in self.interestingPaths:
            self.interestingPaths.append(path)
            print("t is interesting")
            return True

        return False

    async def fuzz(self):
        while len(self.seedQ) >= 1:  # and timeout?
            t = self.ChooseNext()
            E = self.AssignEnergy(t)
            for i in range(1, E):
                t_prime = self.mutate_t(t)
                crashOrBug, t_prime_coverage_data, covered_lines = (
                    await self.runTestRevealsCrashOrBug(t_prime)
                )
                if crashOrBug:
                    self.failureQ.append(t_prime)
                    for i, tup in enumerate(self.pathCoverage):
                        if t_prime_coverage_data == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] += 1
                            self.pathCoverage[0][1] += 1
                            changed = True
                        if i == len(self.pathCoverage) - 1 and changed != True:
                            self.pathCoverage.append((t_prime_coverage_data, 1))
                elif self.isInteresting(t_prime_coverage_data) == True:
                    self.seedQ.append((t_prime, t_prime_coverage_data, covered_lines))
                    for i, tup in enumerate(self.pathCoverage):
                        if t_prime_coverage_data == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] += 1
                            self.pathCoverage[0][1] += 1
                            changed = True
                        if i == len(self.pathCoverage) - 1 and changed != True:
                            self.pathCoverage.append((t_prime_coverage_data, 1))


def printDict(dictName, dict):
    print("printing " + dictName + "...")
    for k, v in dict.items():
        print("key = {} : value = {}".format(k, v))
