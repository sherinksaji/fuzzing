import trace
import sys
import json
import hashlib


class CoverageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        

    def __call__(self, request):
        response = self.get_response(request)
        tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix], trace=0, count=1)
        tracer.runfunc(self.get_response, request)
        results = tracer.results()
        coverage_data = results.counts
        self.process_response(coverage_data)
        # print('coverage response', coverage_data)
        return response

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
            "H": {"start": 128, "end": float("inf")}
        }
        
        for key in buckets:
            if taken >= buckets[key]["start"] and taken <= buckets[key]["end"]:
                bucket_index = key
        return bucket_index

    def process_response(self, response):
        branches = []
        path_len = 0
        for key in response:
            branch_str = key[0] + "_" + str(key[1]) + "_" + self.get_bucket_index(response[key])
            branches.append(branch_str)
            path_len += 1
        branches.sort()
        # print("".join(branches))
        hash_object = hashlib.md5(",".join(branches).encode())
        short_string = hash_object.hexdigest()
        
        with open("coverage.txt", "a") as file:  # Using "a" to append to the file
            file.write(short_string+"\n")
        
        
