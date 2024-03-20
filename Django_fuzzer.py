from AFL_base import AFL_Fuzzer
import subprocess
import random
from djangoInput import DjangoInput


class DjangoFuzzer(AFL_Fuzzer):
    class MyFuzzer(AFL_Fuzzer):
        def __init__(self):
            super().__init__()

        @Override
        def mutateDjangoInput(self, t: DjangoInput):
            randomNumber = random.randint(0, 5)
            if randomNumber == 0:
                t.name = self.mutate_str(t.name)

            elif randomNumber == 1:
                t.info = self.mutate_str(t.info)

            elif randomNumber == 2:
                t.price = str(random.randint(1, 100))

            elif randomNumber == 3:
                t.csrftoken = self.mutate_str(t.csrftoken)

            elif randomNumber == 4:
                t.sessionid = self.mutate_str(t.sessionid)
