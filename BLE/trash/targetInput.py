import random
from abc import ABC, abstractmethod


class TargetInput:
    @abstractmethod
    def getNumOfFuzzableInputs():
        pass
