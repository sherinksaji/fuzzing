from copy import deepcopy
from Mutator import Mutator
import random


class AFL_Fuzzer:
    def __init__(self):
        self.seedQ = []
        self.failureQ = []
        self.branchBucketDict = {}

    def ChooseNext(self):
        # insert function
        # use self.seedQ
        
        # Handle the case when seedQ is empty
        if not self.seedQ:
            return None
        # Find the input t with the maximum path coverage
        next_input = max(self.seedQ, key=self.seedQ.get)
        # Remove the extracted input from seedQ
        del self.seedQ[next_input]
        # Return the chosen input t
        return next_input

    def AssignEnergy(self, t):
        # insert function

        return True

    def MutateInput(self, t):
        # insert function
        mutator = Mutator()
        #probabilities to be determined after pilot fuzzing, these are just test values set
        mutator_probabilities = [0.1, 0.1, 0.2, 0.2, 0.2, 0.1, 0.1]
        selected_mutator = random.choices(mutator.mutators, weights=mutator_probabilities)[0]
        mutated_input = selected_mutator(t)
        return mutated_input

    def getBranches(self, t_prime_path):
        branches = []
        for i in range(len(t_prime_path) - 1):
            branches.append((t_prime_path[i], t_prime_path[i + 1]))
        return branches

    def getBranchCountDict(self, branches):
        branchCountDict = {}
        for branch in branches:
            if branch not in branchCountDict.keys():
                branchCountDict[branch] = 1
            else:
                branchCountDict[branch] += 1
        return branchCountDict

    def newThresholdReachedUpdate(self, branchCountDict):
        # bucket_threshold = [1,2,3,4-7,8-15,16-31,32-127,128+]
        prevBucketDict = deepcopy(self.branchBucketDict)
        for k, v in branchCountDict.items():
            if v == 1:
                self.branchBucketDict[k] = "1"
            elif v == 2:
                self.branchBucketDict[k] = "2"
            elif v == 3:
                self.branchBucketDict[k] = "3"
            elif v >= 4 and v <= 7:
                self.branchBucketDict[k] = "4-7"
            elif v >= 8 and v <= 15:
                self.branchBucketDict[k] = "8-15"
            elif v >= 16 and v <= 31:
                self.branchBucketDict[k] = "16-31"
            elif v >= 32 and v <= 127:
                self.branchBucketDict[k] = "32-127"
            elif v >= 128:
                self.branchBucketDict[k] = "128+"

        return prevBucketDict != self.branchBucketDict

    def isInteresting(self, t_prime_path):
        # insert function
        # -store and update pathBranchCountDictionary key:value→ path:count
        # -store and update pathBranchBucketDictionary key:value→path:bucket
        # -if a bucket update was made→return true else return false
        branches = self.getBranches(t_prime_path)
        branchCountDict = self.getBranchCountDict(branches)
        return self.newThresholdReached(branchCountDict)

    def runTestRevealsCrashOrBug(self, t_prime):
        # insert
        crashOrBug = True
        t_prime_path = ["A", "B", "C", "B", "C", "A"]
        return crashOrBug, t_prime_path

    def fuzz(self):
        while self.seedQ[0] != None:  # and timeout?
            t = self.ChooseNext()
            E = self.AssignEnergy(t)
            for i in range(1, E):
                t_prime = self.MutateInput(t)
                crashOrBug, t_prime_path = self.runTestRevealsCrashOrBug(t_prime)
                if crashOrBug:
                    self.FailureQ.append(t_prime)
                elif self.isInteresting(t_prime_path) == True:
                    self.SeedQ.append[(t_prime, t_prime_path)]


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


# tests for isinterersting
# aflFuzzer = AFL_Fuzzer()
# path = ["A", "B", "C", "B", "C", "A"]
# for i in range(10):
#     branches = aflFuzzer.getBranches(path)
#     # print("branches : ", branches)
#     branchCountDict = aflFuzzer.getBranchCountDict(branches)
#     printDict("branchCountDict", branchCountDict)
#     print("updateOccurred : ", aflFuzzer.newThresholdReachedUpdate(branchCountDict))
#     printDict("branchBucketDict", aflFuzzer.branchBucketDict)
#     path += path[1:]
#     print(
#         """

#             ----One test over ---

#            """
#     )
