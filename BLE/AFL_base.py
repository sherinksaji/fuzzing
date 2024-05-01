from copy import deepcopy
from mutator import Mutator
import hashlib
from abc import ABC, abstractmethod
import pandas as pd
import matplotlib.pyplot as plt
import time


class AFL_Fuzzer(ABC):
    def __init__(self, seedQ):
        self.seedQ = seedQ
        self.failureQ = []
        self.pathCoverage = []
        self.pathCoverage.append(["totalPaths", 0])
        self.interestingPaths = []
        self.mutator = Mutator()
        self.numberOfTimes = 1
        self.numberOfCrashOrBug = 0
        self.timeTakenForFirstCrashOrBugFound = 0
        self.numTests = 0
        self.testCases = []
        self.rq1_df = pd.DataFrame(
            columns=["Number of interesting test cases", "Number of tests"]
        )
        self.sumOfRunTestTimes = 0

    def ChooseNext(self):
        next = self.seedQ.pop(0)
        return next[0]

    def AssignEnergy(self, t):
        for i in self.pathCoverage:
            if isinstance(i[0], list) and t in i[0]:
                return 512 * self.numberOfTimes * (1 - (i[2] / self.pathCoverage[0][1]))
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

    def isInteresting(self, path):
        # path = self.process_coverage(coverage)
        # print("path : ", path)
        if path not in self.interestingPaths:
            self.interestingPaths.append(path)
            print("t is interesting")
            # print("self.interestingPaths", self.interestingPaths)
            return True
        print("t is not interesting")
        return False

    async def fuzz(self):
        # start of fuzzz
        start_time_of_fuzz = time.perf_counter_ns()
        while len(self.seedQ) >= 1:  # and timeout?
            # print("length of seedQ", len(self.seedQ))
            t = self.ChooseNext()
            E = self.AssignEnergy(t)
            for i in range(1, E):

                t_prime = self.mutate_t(t)
                while t_prime in self.testCases:
                    t_prime = self.mutate_t(t)
                # start-run test
                time_before_run_test = time.perf_counter_ns()
                crashOrBug, t_prime_coverage_data = await self.runTestRevealsCrashOrBug(
                    t_prime
                )
                time_after_run_test = time.perf_counter_ns()
                self.numTests += 1
                # print("self.numTests after incrememting : ", self.numTests)
                duration_run_test = time_after_run_test - time_before_run_test
                self.sumOfRunTestTimes += duration_run_test
                # stop-run test
                # time_taken = stop-start
                path = self.process_coverage(t_prime_coverage_data)
                if crashOrBug:
                    self.numberOfCrashOrBug += 1
                    if self.numberOfCrashOrBug == 1:
                        self.timeTakenForFirstCrashOrBugFound = (
                            time.perf_counter_ns() - start_time_of_fuzz
                        )
                    # first crashOrBug found
                    print("Bug found: adding t to failureQ")
                    for i, tup in enumerate(self.pathCoverage):
                        changed = False
                        if path == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] += 1
                            self.pathCoverage[0][1] += 1
                            changed = True
                        if i == len(self.pathCoverage) - 1 and changed != True:
                            self.pathCoverage.append([[t_prime], path, 1])
                elif self.isInteresting(path) == True:
                    print("adding t to seedQ")
                    self.seedQ.append((t_prime, path))
                    for i, tup in enumerate(self.pathCoverage):
                        changed = False
                        if path == tup[1]:
                            tup[0].append(t_prime)
                            tup[2] += 1
                            self.pathCoverage[0][1] += 1
                            changed = True
                        if i == len(self.pathCoverage) - 1 and changed != True:
                            self.pathCoverage.append([[t_prime], path, 1])
                # rq1

                # rq1_df_new_entry = pd.DataFrame(
                #     [
                #         {
                #             "Number of interesting test cases": len(
                #                 self.interestingPaths
                #             ),
                #             "Number of tests": self.numTests,
                #         }
                #     ]
                # )
                # self.rq1_df = pd.concat(
                #     [self.rq1_df, rq1_df_new_entry], ignore_index=True
                # )
                # self.rq1_df = self.rq1_df.sort_values(by="Number of tests")
                # print(self.rq1_df)

            self.numberOfTimes += 1

        # finish fuzz
        # print("self.numTests", self.numTests)
        # stop_time_of_fuzz = time.perf_counter_ns()

        # rq1

        # self.rq1_df.plot(
        #     x="Number of tests",
        #     y="Number of interesting test cases",
        #     kind="line",
        # )
        # plt.xlabel("#tests")
        # plt.ylabel("#interesting test cases")

        # plt.title("Plot of #interesting test cases vs. #tests")
        # plt.show()

        # rq2
        # print("Average time to run test : ", self.sumOfRunTestTimes / self.numTests)
        # duration_of_fuzz = stop_time_of_fuzz - start_time_of_fuzz
        # duration_of_generate_tests = duration_of_fuzz - self.sumOfRunTestTimes
        # print(
        #     "Average time taken to generate tests : ",
        #     duration_of_generate_tests / self.numTests,
        # )
        # print(
        #     "Time taken for first bug or crash to be found : ",
        #     self.timeTakenForFirstCrashOrBugFound,
        # )


def printDict(dictName, dict):
    print("printing " + dictName + "...")
    for k, v in dict.items():
        print("key = {} : value = {}".format(k, v))
