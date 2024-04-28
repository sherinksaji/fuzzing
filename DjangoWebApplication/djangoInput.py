from targetInput import TargetInput


class DjangoInput(TargetInput):
    def __init__(self, name, info, price):
        self.name = name
        self.info = info
        self.price = price

    def getNumOfFuzzableInputs(self):
        return 3

    def getFormData(self):
        form_data = {"name": self.name, "info": self.info, "price": self.price}
        return form_data

    def getHeader(
        self,
    ):  # i just put the header info here, but i understand its not for mutation for this app
        csrftoken = "5vvs6151ScRQGpdMlKAf8FAFERO67MmK"
        sessionid = "c35o5m7xkymbjdtcu9k916f8jfj2f8x7"
        header = {"Cookie": "csrftoken=" + csrftoken + "; sessionid=" + sessionid}
        return header

    def __str__(self):
        return f"""
         name = {self.name}
         info = {self.info}
         price = {self.price}

        getNumOfFuzzableInputs={self.getNumOfFuzzableInputs()}
        

 """


djangoInput = DjangoInput("sh", "abcd", "10")
print(djangoInput)
