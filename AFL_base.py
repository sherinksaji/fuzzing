SeedQ = []
FailureQ = []
revealsCrashOrBug = 1


def ChooseNext(SeedQ):
    #insert function
    return True

def AssignEnergy(t):
    #insert function
    return True

def MutateInput(t):
    #insert function
    return True

def isInteresting(t_prime):
    #insert function
    return True


def Main():
    while SeedQ[0] != None: # and timeout? 
        t = ChooseNext(SeedQ)
        E = AssignEnergy(t)
        for i in range (1, E):
            t_prime = MutateInput(t)
            if t_prime == 1:
                FailureQ.append(t_prime)
            elif isInteresting(t_prime) == True:
                SeedQ.append(t_prime)
        


