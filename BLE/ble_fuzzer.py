import requests
import random
import json
import coverage
import os
import subprocess
import time
import string
import logging
import asyncio
import sys
import os
from binascii import hexlify
import random
import struct
from bumble.device import Device, Peer
from bumble.host import Host  # Host controller interface?
from bumble.gatt import show_services, Characteristic
from bumble.att import Attribute
from bumble.core import ProtocolError
from bumble.controller import Controller  # controller layer
from bumble.link import LocalLink  # link layer
from bumble.transport import open_transport_or_link
from bumble.utils import AsyncRunner
from bumble.colors import color

from mutator import Mutator
from AFL_base import AFL_Fuzzer
import subprocess
import random
from bleInput import BLE_ReadATT_Input, BLE_WriteATT_Input


class BLE_Fuzzer(AFL_Fuzzer):

    def __init__(self, target, attributes):
        super().__init__()
        self.target = target
        self.init_seedQ(attributes)

        # print("init>first t : ", self.seedQ[0][0])

    def init_seedQ(self, attributes):
        self.seedQ = []
        for attribute in attributes:
            self.seedQ.append((BLE_ReadATT_Input(attribute), None))
            self.seedQ.append((BLE_WriteATT_Input(attribute, b"hello123"), None))
            self.seedQ.append(
                (BLE_WriteATT_Input(attribute, bytearray([1, 2, 3])), None)
            )
            self.seedQ.append((BLE_WriteATT_Input(attribute, 12), None))
            self.seedQ.append((BLE_WriteATT_Input(attribute, "hello123"), None))

    def get_write_input(self, t):
        write_input = None
        for tuplet in self.seedQ:
            t_tuplet = tuplet[0]
            if isinstance(t_tuplet, BLE_WriteATT_Input):
                if t_tuplet.attribute.handle == t.attribute.handle:
                    write_input = t_tuplet.writeInput

        if write_input == None:
            return self.seedQ[-1][1]
        else:
            return write_input

    def mutate_t(self, t, index):
        # change t's type
        mutator = Mutator()
        if random.choice([True, True, True, False]):
            pass
        else:
            if isinstance(t, BLE_WriteATT_Input):
                new_t = BLE_ReadATT_Input(t.attribute)
                return new_t

            elif isinstance(t, BLE_WriteATT_Input):
                new_t = BLE_WriteATT_Input(t.attribute, self.get_write_input(t))
                return new_t

        if isinstance(t, BLE_ReadATT_Input):
            t.attribute.handle = mutator.mutate_number(t.attribute.handle)

        elif isinstance(t, BLE_WriteATT_Input):
            if random.choice([True, False, False, False]):
                t.attribute.handle = mutator.mutate_number(t.attribute.handle)
            else:

                if isinstance(t.writeInput, bytearray):
                    t.writeInput = mutator.mutate_bytearray(t.writeInput)
                elif isinstance(t.writeInput, bytes):
                    t.writeInput = mutator.mutate_bytestring(t.writeInput)
                elif isinstance(t.writeInput, int):

                    t.writeInput = mutator.mutate_number(t.writeInput)
                elif isinstance(t.writeInput, str):
                    t.writeInput = mutator.mutate_str(t.writeInput)

        return t

    async def write_target(self, attribute, bytes_to_write):
        # Write

        try:

            if type(attribute.handle) == int:
                attribute_handle_str = f"{attribute.handle:04X}"
            else:
                attribute_handle_str = attribute.handle

            await self.target.write_value(attribute, bytes_to_write, True)
            # print(
            #     color(
            #         f"[OK] WRITE Handle 0x{attribute_handle_str} --> Trying invalid, Val = {bytes_to_write}",
            #         "green",
            #     )
            # )
            print(
                color(
                    f"[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}",
                    "green",
                )
            )

            return True
        except ProtocolError as error:
            print(
                color(
                    f"[!]  Cannot write attribute 0x{attribute_handle_str}:", "yellow"
                ),
                error,
            )
        except ValueError as value_error:
            print(
                color(
                    f"[!] Cannot write attribute 0x{attribute_handle_str}. Value Error:{value_error}",
                    "yellow",
                )
            )
        except TimeoutError:
            print(
                color(
                    f"[X] Cannot write attribute 0x{attribute_handle_str}.Write Timeout",
                    "red",
                )
            )
        except TypeError as type_error:
            print(
                color(
                    f"[!] Cannot write attribute 0x{attribute_handle_str}.Type Error:",
                    "yellow",
                ),
                type_error,
            )
        except struct.error as struct_error:
            print(
                color(
                    f"Cannot write attribute 0x{attribute_handle_str}.[!] Struct Error:",
                    "yellow",
                ),
                struct_error,
            )

        return False

    async def read_target(self, attribute):
        # Read

        if type(attribute.handle) == int:
            attribute_handle_str = f"{attribute.handle:04X}"
        else:
            attribute_handle_str = attribute.handle

        try:
            read = await self.target.read_value(attribute)
            value = read.decode("latin-1")
            print(
                color(
                    f"[OK] READ  Handle 0x{attribute_handle_str} <-- Bytes={len(read):02d}, Val={read.hex()}",
                    "cyan",
                )
            )
            return True
        except ProtocolError as error:
            print(
                color(
                    f"[!]  Cannot read attribute 0x{attribute_handle_str}:", "yellow"
                ),
                error,
            )

        except struct.error as struct_error:
            print(
                color(
                    f"[!] Cannot read attribute 0x{attribute_handle_str}. Struct Error:",
                    "yellow",
                ),
                struct_error,
            )
        except TimeoutError:
            print(
                color(
                    f"[!] Cannot read attribute 0x{attribute_handle_str}. Read Timeout"
                )
            )

        return False

    async def runTestRevealsCrashOrBug(self, t_prime):
        print("running on input: ", t_prime)
        if isinstance(t_prime, BLE_ReadATT_Input):
            revealsCrashOrBug = await self.read_target(t_prime.attribute)
        elif isinstance(t_prime, BLE_WriteATT_Input):
            revealsCrashOrBug = await self.write_target(
                t_prime.attribute, t_prime.writeInput
            )
        coverage_data = {}

        return revealsCrashOrBug, coverage_data
