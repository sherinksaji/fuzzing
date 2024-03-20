class DjangoInput:
    def __init__(self, name, info, price, csrftoken, sessionid):
        self.name = name
        self.info = info
        self.price = price
        self.csrftoken = csrftoken
        self.sessionid = sessionid

    def getFormData(self):
        form_data = {"name": self.name, "info": self.info, "price": self.price}
        return form_data

    def getHeader(self):
        header = {
            "Cookie": "csrftoken=" + self.csrftoken + "; sessionid=" + self.sessionid
        }
        return header
