from copy import deepcopy
import string
import random
from mutator import Mutator

import random
from abc import ABC, abstractmethod


# copy this file into which ever directory u want to use yr child fuzzer in
# u probably want to use your child fuzzer within the directory of the target u are fuzzing
class AFL_Fuzzer(ABC):
    def __init__(self):
        self.seedQ = [None]
        self.failureQ = []
        self.executed_lines_history = []
        self.mutator = Mutator()
        self.pathCoverage = []
        self.pathCoverage.append(('totalpaths', 0))

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
                return (512*(1-(i[2]/self.pathCoverage[0][1])))   
        
    def generate_random_str(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        result_str = "".join(random.choice(characters) for _ in range(self.len_limit))
        self.seedQ.append(result_str)

        return result_str

    def mutate_str(self, input):
        return self.mutator.mutate_str(input_str=input)

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

    def isInteresting(self, coverage_data):
        isInteresting = True
        executed_lines = {}
        for filename, file_data in coverage_data["files"].items():
            executed_lines[filename] = set(file_data["executed_lines"])

        if len(self.executed_lines_history) == 0:

            isInteresting = True
        else:
            for prev_executed_lines in self.executed_lines_history:
                if prev_executed_lines == executed_lines:

                    isInteresting = False
                    break
        self.executed_lines_history.append(executed_lines)
        print("isInteresting : ", isInteresting)
        return isInteresting

    def fuzz(self):
        while len(self.seedQ) >= 1:  # and timeout?
            t = self.ChooseNext()
            E = self.AssignEnergy(t)
            for i in range(1, E):
                # print("i = ", i)
                fuzz_var_index = random.randint(0, t.getNumOfFuzzableInputs())
                t_prime = self.mutate_t(t, fuzz_var_index)
                # print("t_prime after mutate : ", t)
                crashOrBug, t_prime_coverage_data = self.runTestRevealsCrashOrBug(
                    t_prime
                )
                print("t_prime_coverage_data")
                print(t_prime_coverage_data)
                if crashOrBug:
                    self.FailureQ.append(t_prime)
                    for i, tup in enumerate(self.pathCoverage):
                        if t_prime_coverage_data == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] +=1
                            self.pathCoverage[0][1] += 1
                            changed = True
                        if i == len(self.pathCoverage)-1 and changed!=True:
                            self.pathCoverage.append((t_prime_coverage_data, 1))                            
                elif self.isInteresting(t_prime_coverage_data) == True:
                    self.seedQ.append((t_prime, t_prime_coverage_data))
                    if t_prime_coverage_data == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] +=1
                            self.pathCoverage[0][1] += 1
                            changed = True
                    if i == len(self.pathCoverage)-1 and changed!=True:
                            self.pathCoverage.append((t_prime_coverage_data, 1))            
        print("all coverage data")
        for i in range(len(self.seedQ)):
            print(self.seedQ[i][1])


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