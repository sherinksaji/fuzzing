from targetInput import TargetInput

class CoAPInput(TargetInput):

    def __init__(self, payload, header, resourcepath,type, method):
        self.payload = payload
        self.header = header
        self.resourcepath = resourcepath
        self.msgtype=type
        self.method=method

    def print_CoAPInput(self):
        input_obj=[self.payload, self.header, self.resourcepath,self.msgtype, self.method]
        print(input_obj)