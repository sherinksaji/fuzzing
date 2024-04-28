import random
from abc import abstractmethod


class TargetInput:
    @abstractmethod
    def getNumOfFuzzableInputs():
        pass