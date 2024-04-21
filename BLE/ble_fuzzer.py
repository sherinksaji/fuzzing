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


# async def stream_output(process, identifier, log_file):
#     """
#     This function asynchronously reads each line of output from the process,
#     writes it to a specified log file, and prints it with an identifier to distinguish between different processes.
#     """
#     # Open the log file in append mode
#     with open(log_file, "a") as file:
#         # Stream both stdout and stderr
#         async for line in process.stdout:
#             decoded_line = line.decode().strip()
#             log_line = f"{identifier} - STDOUT: {decoded_line}\n"
#             print(log_line, end="")  # Print to console
#             file.write(log_line)  # Write to file
#             file.flush()
#         async for line in process.stderr:
#             decoded_line = line.decode().strip()
#             log_line = f"{identifier} - STDERR: {decoded_line}\n"
#             print(log_line, end="")  # Print to console
#             file.write(log_line)  # Write to file
#             file.flush()


# def start_runBLE():

#     subprocess.Popen(["gnome-terminal", "--", "python3", "run_ble_orignal.py"])


# async def run_command(command, identifier, log_file):
#     """
#     This function starts the subprocess for the given command,
#     sets up streaming for its output, and waits for the process to complete.
#     """
#     process = await asyncio.create_subprocess_shell(
#         command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
#     )

#     # Set up tasks to handle stdout and stderr
#     await stream_output(process, identifier, log_file)

#     # Wait for the process to complete and return its exit status
#     return_code = await process.wait()
#     return return_code


def bytes_to_hex_string(byte_list):
    return "".join([format(b, "02x") for b in byte_list])


def write_t_prime(bytes_list):
    hex_string = bytes_to_hex_string(bytes_list)
    with open("t_prime.txt", "w") as file:
        file.write(hex_string)


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


def start_process_in_new_terminal(command, window_title=""):
    """
    Starts a command in a new GNOME Terminal window.
    """
    subprocess.Popen(
        ["gnome-terminal", "--title", window_title, "--", "bash", "-c", command]
    )


def start_ble_original():
    """
    Starts run_ble_original.py in a new GNOME Terminal window.
    """
    start_process_in_new_terminal("python3 run_ble_original.py", "BLE Original")


def start_zephyr():
    """
    Starts zephyr.exe in a new GNOME Terminal window.
    """
    zephyr_command = (
        "GCOV_PREFIX=$(pwd) GCOV_PREFIX_STRIP=3 ./zephyr.exe --bt-dev=127.0.0.1:9000"
    )
    start_process_in_new_terminal(zephyr_command, "Zephyr Execution")


def is9000Alive():
    port_number = 9000
    for conn in psutil.net_connections():
        if conn.laddr.port == port_number and conn.status == "LISTEN":
            # Get the process associated with the connection
            return True

    else:
        return False


def getCoverage(lcov_file):
    lcov_file = "lcov_coverage/" + lcov_file
    file_path = ""
    hit_counts = {}

    with open(lcov_file, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("SF:"):
                file_path = line.split(":", 1)[1]
            elif line.startswith("DA:"):
                parts = line.split(",")
                line_number = parts[0]
                hit_count = int(parts[1])
                if hit_count > 0:
                    hit_counts[(file_path, line_number)] = hit_count

    return hit_counts


def getCoveragePercent(lcov_file):
    lcov_path = "lcov_coverage/" + lcov_file
    with open(lcov_path, "r") as file:
        content = file.readlines()

    total_lines = 0
    covered_lines = 0

    for line in content:
        if line.startswith("DA:"):
            line_info = line.strip().split(",")
            total_lines += 1
            if int(line_info[1]) > 0:  # Check if the line is covered
                covered_lines += 1
    # print("covered_lines : ", covered_lines)
    # print("total_lines : ", total_lines)
    if total_lines > 0:
        coverage_percent = (covered_lines / total_lines) * 100
    else:
        coverage_percent = 0

    return covered_lines


class BLE_Fuzzer(AFL_Fuzzer):
    def __init__(self, seedQ):
        super().__init__(seedQ)

    def mutate_t(self, t_prime):
        mutator = Mutator()
        t_prime = mutator.mutate_byte_list(t_prime)
        return t_prime

    async def runTestRevealsCrashOrBug(self, t_prime):
        runRevealsCrashOrBug = False
        coverage = {}
        print("Running with T_prime:", t_prime)
        cmd1 = "python3 run_ble_original.py"
        cmd2 = "GCOV_PREFIX=$(pwd) GCOV_PREFIX_STRIP=3 ./zephyr.exe --bt-dev=127.0.0.1:9000"
        delete_file("t_prime.txt")
        write_t_prime(t_prime)

        # Define log files for each command
        log_file1 = "output_cmd1.log"
        log_file2 = "output_cmd2.log"

        # Start both commands asynchronously and log their outputs to different files
        # task1 = asyncio.create_task(run_command(cmd1, "RunBLE", log_file1))
        start_ble_original()
        await wait_for_scan_signal()
        start_zephyr()

        while is9000Alive():
            await asyncio.sleep(0.5)
        filename = "result.json"
        result_dict = None
        try:
            with open(filename, "r") as file:
                result_dict = json.load(file)  # Converts JSON to a Python dictionary

        except FileNotFoundError:
            print("File not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON.")

        crash = result_dict["crash"]

        bug = result_dict["bug_present"]
        if crash or bug:
            runRevealsCrashOrBug = True
        lcov_file = result_dict["lcovFilename"]
        coverage = getCoverage(lcov_file)
        covered_lines = getCoveragePercent(lcov_file)

        return runRevealsCrashOrBug, coverage, covered_lines


# async def run_fuzzer():
#     count = 0
#     t_prime = [0x01]
#     while count < 10:

#         mutator = Mutator()
#         t_prime = mutator.mutate_byte_list(t_prime)
#         await runTestRevealsCrashOrBug(t_prime)

#         count += 1


# Call the asynchronous function
delete_file("bugAndCrashReport.txt")
delete_file("result.json")
delete_file("scan_signal.txt")
seedQ = [([0x01], None, None)]
bleFuzzer = BLE_Fuzzer(seedQ)
asyncio.run(bleFuzzer.fuzz())
