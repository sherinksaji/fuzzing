#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
import asyncio
import sys
import os
from binascii import hexlify
import time
import subprocess
import os
import signal
import glob
import shutil
import psutil
import hashlib
from bumble.device import Device, Peer
from bumble.host import Host  # Host controller interface?
from bumble.gatt import show_services, Characteristic
from bumble.att import Attribute
from bumble.core import ProtocolError, TimeoutError

from bumble.controller import Controller  # controller layer
from bumble.link import LocalLink  # link layer
from bumble.transport import open_transport_or_link
from bumble.utils import AsyncRunner
from bumble.colors import color
import bumble
from ble_fuzzer import BLE_Fuzzer
import time
import random
import struct
from mutator import Mutator
from AFL_base import AFL_Fuzzer
from bleInput import BLE_ByteList_Input
from pyee import EventEmitter
from bumble.hci import HCI_REMOTE_USER_TERMINATED_CONNECTION_ERROR


async def write_target(target, attribute, bytes):
    # Write
    try:
        bytes_to_write = bytearray(bytes)
        print("bytes_to_write : ", bytes_to_write)
        await target.write_value(attribute, bytes_to_write, True)
        print(
            color(
                f"[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}",
                "green",
            )
        )
        return True
    except ProtocolError as error:
        print(
            color(f"[!]  Cannot write attribute 0x{attribute.handle:04X}:", "yellow"),
            error,
        )

    except asyncio.exceptions.TimeoutError:
        print(color("[X] Write Timeout", "red"))
        # Handle the GATT timeout error gracefully here

    except TimeoutError:
        print(color("[X] Write Timeout", "red"))
        zephyr_died()
    return False


async def read_target(target, attribute):
    # Read
    try:
        read = await target.read_value(attribute)
        value = read.decode("latin-1")
        print(
            color(
                f"[OK] READ  Handle 0x{attribute.handle:04X} <-- Bytes={len(read):02d}, Val={read.hex()}",
                "cyan",
            )
        )
        return value
    except ProtocolError as error:
        print(
            color(f"[!]  Cannot read attribute 0x{attribute.handle:04X}:", "yellow"),
            error,
        )
    except TimeoutError:
        print(color("[!] Read Timeout"))

    return None


# -----------------------------------------------------------------------------
class TargetEventsListener(Device.Listener):

    def __init__(self, t_prime):
        super().__init__()
        self.t_prime = t_prime
        self.communicationOver = False

    got_advertisement = False
    advertisement = None
    connection = None

    def on_advertisement(self, advertisement):

        print(
            f'{color("Advertisement", "cyan")} <-- '
            f'{color(advertisement.address, "yellow")}'
        )

        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        print(color(f"[OK] Connected!", "green"))
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        print("=== Discovering services")
        target = Peer(connection)
        attributes = []
        await target.discover_services()
        for service in target.services:
            attributes.append(service)
            await service.discover_characteristics()
            for characteristic in service.characteristics:
                attributes.append(characteristic)
                await characteristic.discover_descriptors()
                for descriptor in characteristic.descriptors:
                    attributes.append(descriptor)

        print(color("[OK] Services discovered", "green"))
        show_services(target.services)
        for attribute in attributes:

            await write_target(target, attribute, self.t_prime.bytelist)
            if zephyr_died == True:
                break

            await read_target(target, attribute)
            if zephyr_died == True:
                break

        print("---------------------------------------------------------------")
        print(color("[OK] Communication Finished", "green"))
        print("---------------------------------------------------------------")
        # ---------------------------------------------------

        self.communicationOver = True


# -----------------------------------------------------------------------------


def start_zephyr(terminal_emulator):
    # Set GCOV_PREFIX and GCOV_PREFIX_STRIP environment variables
    os.environ["GCOV_PREFIX"] = os.getcwd()
    os.environ["GCOV_PREFIX_STRIP"] = "3"

    # Start zephyr.exe in a new terminal window using the specified terminal emulator
    print(terminal_emulator)

    subprocess.Popen(
        [terminal_emulator, "--", "./zephyr.exe", "--bt-dev=127.0.0.1:9000"]
    )


# Find pid of zephyr.exe
def find_pid(process_name):
    for pid in os.listdir("/proc"):
        try:
            if pid.isdigit():
                cmdline = open(os.path.join("/proc", pid, "cmdline"), "rb").read()
                if process_name in cmdline.decode():
                    return pid
        except IOError:
            print("IOError")
            continue
    return None


def zephyr_died():
    zephyr_pid = find_pid("zephyr.exe")

    # Kill the process with the obtained pid
    if zephyr_pid:
        print("Zephyr still alive")
        return False
    else:
        print("Zephyr died")
        return True


def delete_gcda_files():
    # Define the directory where .gcda files are located
    gcda_files_directory = "~/STV-Project/BLE"

    # Expand the tilde (~) to the user's home directory
    gcda_files_directory = os.path.expanduser(gcda_files_directory)

    # List to store .gcda files
    gcda_files = []

    # Recursively walk through the directory
    for root, dirs, files in os.walk(gcda_files_directory):
        for file in files:
            if file.endswith(".gcda"):
                gcda_files.append(os.path.join(root, file))

    for gcda_file in gcda_files:
        os.remove(gcda_file)
    print("Deleted generated .gcda files.")


def get_lcov():

    zephyr_pid = find_pid("zephyr.exe")

    # Kill the process with the obtained pid
    if zephyr_pid:
        print("gg to kill")
        os.kill(int(zephyr_pid), signal.SIGTERM)

    # # Capture code coverage using lcov
    fileName = "lcov_" + str(time.time_ns()) + ".info"
    fullDir = os.path.join("lcov_coverage", fileName)

    lcov_capture_command = (
        "lcov --capture --directory ./ --output-file "
        + fullDir
        + " -q --rc lcov_branch_coverage=1"
    )
    os.system(lcov_capture_command)

    # Summarize code coverage
    lcov_summary_command = "lcov --rc lcov_branch_coverage=1 --summary " + fullDir
    os.system(lcov_summary_command)


def kill9000():
    port_number = 9000
    for conn in psutil.net_connections():
        if conn.laddr.port == port_number and conn.status == "LISTEN":
            # Get the process associated with the connection
            process = psutil.Process(conn.pid)
            # Terminate the process
            process.terminate()
            print(
                f"Process with PID {conn.pid} using port {port_number} has been terminated."
            )
            break
    else:
        print(f"No process found using port {port_number}.")


# -----------------------------------------------------------------------------
async def main():

    revealsCrashOrBug = False
    t_prime = BLE_ByteList_Input([0x01])
    tcp_server = "tcp-server:127.0.0.1:9000"
    print(">>> Waiting connection to HCI...")
    async with await open_transport_or_link(tcp_server) as (hci_source, hci_sink):
        print(">>> Connected")

        # Create a local communication channel between multiple controllers
        link = LocalLink()

        # Create a first controller for connection with host interface (Zephyr)
        zephyr_controller = Controller(
            "Zephyr", host_source=hci_source, host_sink=hci_sink, link=link
        )

        # Create our own device (tester central) to manage the host BLE stack
        device = Device.from_config_file("tester_config.json")
        # Create a host for the second controller
        device.host = Host()
        # Create a second controller for connection with this test driver (Bumble)
        device.host.controller = Controller("Fuzzer", link=link)
        # Connect class to receive events during communication with target
        device.listener = TargetEventsListener(t_prime)

        # Start BLE scanning here
        await device.power_on()
        await device.start_scanning()  # this calls "on_advertisement"

        print("Waiting Advertisment from BLE Target")
        device.listener.t_prime = t_prime
        start_zephyr("gnome-terminal")
        while device.listener.got_advertisement is False:
            await asyncio.sleep(0.5)
        await device.stop_scanning()  # Stop scanning for targets

        print(color("\n[OK] Got Advertisment from BLE Target!", "green"))
        target_address = device.listener.advertisement.address

        # Start BLE connection here
        print(f"=== Connecting to {target_address}...")
        await device.connect(target_address)  # this calls "on_connection"

        while not device.listener.communicationOver:
            await asyncio.sleep(0.5)

        if zephyr_died:
            revealsCrashOrBug = True

        get_lcov()
        delete_gcda_files()

        kill9000()


# -----------------------------------------------------------------------------
logging.basicConfig(level=os.environ.get("BUMBLE_LOGLEVEL", "INFO").upper())
asyncio.run(main())
