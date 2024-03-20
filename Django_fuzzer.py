from AFL_base import AFL_Fuzzer
import subprocess
import random
from djangoInput import DjangoInput


class DjangoFuzzer(AFL_Fuzzer):
    class MyFuzzer(AFL_Fuzzer):
        def __init__(self):
            super().__init__()

        @Override
        def mutateDjangoInput(self, t: DjangoInput, index):
            if index == 0:
                t.name = self.mutate_str(t.name)

            elif index == 1:
                t.info = self.mutate_str(t.info)

            elif index == 2:
                t.price = str(random.randint(1, 100))

            elif index == 3:
                t.csrftoken = self.mutate_str(t.csrftoken)

            elif index == 4:
                t.sessionid = self.mutate_str(t.sessionid)
