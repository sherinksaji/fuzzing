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
import signal
import time
from mutator import Mutator
from AFL_base import AFL_Fuzzer
import subprocess
import random
import psutil
from bleInput import BLE_ReadATT_Input, BLE_WriteATT_Input, BLE_ByteList_Input


class BLE_Fuzzer(AFL_Fuzzer):

    def __init__(self):
        super().__init__()
        self.init_seedQ()

        # print("init>first t : ", self.seedQ[0][0])

    def init_seedQ(self):
        self.seedQ = []
        self.seedQ.append((BLE_ByteList_Input([0x01]), None))

    def mutate_t(self, t, index):
        mutator = Mutator()
        new_bytelist = [0x01]  # mutator.mutate_byte_list(t.bytelist)
        t_prime = BLE_ByteList_Input(new_bytelist)
        return t_prime

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
        zephyr_pid = BLE_Fuzzer.find_pid("zephyr.exe")

        # Kill the process with the obtained pid
        if zephyr_pid:
            print("Zephyr still alive")
            return False
        else:
            print("Zephyr died")
            return True

    def delete_file(file_path):
        """Delete a file if it exists."""
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")

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

        zephyr_pid = BLE_Fuzzer.find_pid("zephyr.exe")

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

    def is9000Alive():
        port_number = 9000
        for conn in psutil.net_connections():
            if conn.laddr.port == port_number and conn.status == "LISTEN":
                # Get the process associated with the connection
                return True
            else:
                print("9000 died")
                return False

    async def wait_for_scan_signal():
        """Waits for the scanning signal from run_ble_original.py."""
        while True:
            if os.path.exists("scan_signal.txt"):
                with open("scan_signal.txt", "r") as signal_file:
                    if signal_file.read().strip() == "scanning":
                        print("Scan signal detected, proceeding with zephyr.exe.")
                        return
            else:
                print("Waiting for scan signal...")
                await asyncio.sleep(0.5)  # Wait a bit before checking again

    async def wait_for_communication_over_signal():
        """Waits for the communication over signal from run_ble_original.py."""
        #  with open("communication_over_signal.txt", "w") as signal_file:
        #     signal_file.write("communication over")
        while True:
            if os.path.exists("communication_over_signal.txt"):
                with open("communication_over_signal.txt", "r") as signal_file:
                    if signal_file.read().strip() == "communication over":
                        print(
                            "Communication signal detected. Proceeding to coverage and shut down"
                        )
                        return
            else:
                await asyncio.sleep(0.5)  # Wait a bit before checking again

    async def run_command(command):
        # Create a subprocess using asyncio to handle it asynchronously
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for the process to complete and capture stdout and stderr
        stdout, stderr = await process.communicate()

        # Return both outputs and the exit status
        return stdout.decode(), stderr.decode(), process.returncode

    async def stream_output(process, identifier):
        """
        This function asynchronously reads each line of output from the process,
        and prints it with an identifier to distinguish between different processes.
        """
        async for line in process.stdout:
            print(f"{identifier} - STDOUT: {line.decode().strip()}")
        # Optionally handle stderr in a similar way if needed.

    async def run_command(command, identifier):
        """
        This function starts the subprocess for the given command,
        sets up streaming for its output, and waits for the process to complete.
        """
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Set up tasks to handle stdout (and optionally stderr)
        await asyncio.gather(BLE_Fuzzer.stream_output(process, identifier))

        # Wait for the process to complete and return its exit status
        return_code = await process.wait()
        return return_code

    async def runTestRevealsCrashOrBug(self, t_prime):
        """
        This function runs two commands concurrently and streams their outputs.
        It uses identifiers to distinguish outputs from each subprocess.
        """

        cmd1 = "python3 run_ble_original.py"
        cmd2 = "GCOV_PREFIX=$(pwd) GCOV_PREFIX_STRIP=3 ./zephyr.exe --bt-dev=127.0.0.1:9000"

        # Start both commands asynchronously
        task1 = asyncio.create_task(BLE_Fuzzer.run_command(cmd1, "CMD1"))
        await BLE_Fuzzer.wait_for_scan_signal()
        task2 = asyncio.create_task(BLE_Fuzzer.run_command(cmd2, "CMD2"))
        # Wait for both tasks to complete
        # await BLE_Fuzzer.wait_for_communication_over_signal()

        await asyncio.gather(task1, task2)

        # BLE_Fuzzer.delete_file("communication_over_signal.txt")

        runRevealsCrashOrBug = True
        coverage = {}
        return runRevealsCrashOrBug, coverage


async def run_fuzzer():
    bleFuzzer = BLE_Fuzzer()
    t_prime = BLE_ByteList_Input([0x01])
    await bleFuzzer.runTestRevealsCrashOrBug(t_prime)


# Call the asynchronous function
asyncio.run(run_fuzzer())
