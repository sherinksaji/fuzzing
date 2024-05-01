#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
import asyncio
import sys
import os
import glob
import time
import signal
import json
from binascii import hexlify
import psutil
from bumble.device import Device, Peer
from bumble.host import Host
from bumble.gatt import show_services
from bumble.core import ProtocolError, TimeoutError
from bumble.controller import Controller
from bumble.link import LocalLink
from bumble.transport import open_transport_or_link
from bumble.utils import AsyncRunner
from bumble.colors import color

result_dict = {}
result_dict["bug_present"] = False


async def write_target(target, attribute, bytes, PermissionsAct):
    # Write
    str_attribute = str(attribute)
    split = str_attribute.split(",")
    handle = f"0x{attribute.handle:04X}"
    try:
        bytes_to_write = bytearray(bytes)
        await target.write_value(attribute, bytes_to_write, True)
        print(
            color(
                f"[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}",
                "green",
            )
        )
        # if split[0][0] == "S" and PermissionsAct[handle][1].find("WRITE") == -1:
        #     print(
        #         color(
        #             f"BUG FOUND at WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}. This service of handle 0x{attribute.handle:04X} does not have WRITE permission\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND at WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}. This service of handle 0x{attribute.handle:04X} does not have WRITE permission\n"
        #     )

        # elif split[0][0] == "D" and PermissionsAct[handle][1].find("WRITE") == -1:
        #     print(
        #         color(
        #             f"BUG FOUND at WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}. This descriptor of handle 0x{attribute.handle:04X} does not have WRITE permission\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}.This descriptor of handle 0x{attribute.handle:04X} does not have WRITE permission\n"
        #     )

        if split[0][0] == "C" and (
            PermissionsAct[handle][1].find("|WRITE|") == -1
            or (
                PermissionsAct[handle][1].find("|WRITE") == -1
                and PermissionsAct[handle][1].find("|WRITE_") != -1
            )
        ):
            print(
                color(
                    f"BUG FOUND. WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}.This characteristic of handle 0x{attribute.handle:04X} does not have WRITE permission\n",
                    "red",
                )
            )
            result_dict["bug_present"] = True
            addToCrashAndBugReport(
                f"BUG FOUND. WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}.This characteristic of handle 0x{attribute.handle:04X} does not have WRITE permission\n"
            )

        return True
    except ProtocolError as error:
        print(
            color(f"[!]  Cannot write attribute 0x{attribute.handle:04X}:", "yellow"),
            error,
        )
        # if split[0][0] == "S" and PermissionsAct[handle][1].find("WRITE") != -1:
        #     print(
        #         color(
        #             f"BUG FOUND at WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}. This service of handle 0x{attribute.handle:04X} has WRITE permission, but is not being WRITTEN to\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND at WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}. This service of handle 0x{attribute.handle:04X} has WRITE permission, but is not being WRITTEN to\n"
        #     )

        # elif split[0][0] == "D" and PermissionsAct[handle][1].find("WRITE") != -1:
        #     print(
        #         color(
        #             f"BUG FOUND. This descriptor of handle 0x{attribute.handle:04X} has WRITE permission, but is not being WRITTEN to\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. This descriptor of handle 0x{attribute.handle:04X} has WRITE permission, but is not being WRITTEN to\n"
        #     )

        # if split[0][0] == "C" and (
        #     PermissionsAct[handle][1].find("|WRITE|") != -1
        #     or (
        #         PermissionsAct[handle][1].find("|WRITE") != -1
        #         and PermissionsAct[handle][1].find("|WRITE_|") == -1
        #     )
        # ):
        #     print(
        #         color(
        #             f"BUG FOUND. This characteristic of handle 0x{attribute.handle:04X} has WRITE permission, but is not being WRITTEN to\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. This characteristic of handle 0x{attribute.handle:04X} has WRITE permission, but is not being WRITTEN to\n"
        #     )

    except asyncio.exceptions.TimeoutError:
        print(color("[X] Write Timeout", "red"))
        # Handle the GATT timeout error gracefully here
        zephyr_died()
        if zephyr_died == False:
            kill_all_zephyr_processes()
        zephyr_died()
        addToCrashAndBugReport(
            f"BUG FOUND. asyncio.exceptions.TimeoutError for 0x{attribute.handle:04X}\n"
        )

    except TimeoutError:
        print(color("[X] Write Timeout", "red"))
        addToCrashAndBugReport(
            f"BUG FOUND. bumble.core.TimeoutError for 0x{attribute.handle:04X}. Zephyr may have crashed.\n"
        )
        zephyr_died()
        if zephyr_died == False:
            kill_all_zephyr_processes()
        zephyr_died()

    return False


def addToCrashAndBugReport(stmt):
    f = open("bugAndCrashReport.txt", "a")
    f.write(stmt)
    f.close()


async def read_target(target, attribute, PermissionsAct):
    # Read
    str_attribute = str(attribute)
    split = str_attribute.split(",")
    handle = f"0x{attribute.handle:04X}"
    try:
        read = await target.read_value(attribute)
        value = read.decode("latin-1")

        print(
            color(
                f"[OK] READ  Handle 0x{attribute.handle:04X} <-- Bytes={len(read):02d}, Val={read.hex()}",
                "cyan",
            )
        )

        # if split[0][0] == "S" and PermissionsAct[handle][1].find("READ") == -1:
        #     print(
        #         color(
        #             f"BUG FOUND. This service of handle 0x{attribute.handle:04X} does not have READ permission\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. This service of handle 0x{attribute.handle:04X} does not have READ permission\n"
        #     )

        # elif split[0][0] == "D" and PermissionsAct[handle][1].find("READ") == -1:
        #     print(
        #         color(
        #             f"BUG FOUND. This descriptor of handle 0x{attribute.handle:04X} does not have READ permission\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. This descriptor of handle 0x{attribute.handle:04X} does not have READ permission\n"
        #     )

        if split[0][0] == "C" and PermissionsAct[handle][1].find("READ") == -1:
            print(
                color(
                    f"BUG FOUND. This characteristic of handle 0x{attribute.handle:04X} does not have READ permission\n",
                    "red",
                )
            )
            result_dict["bug_present"] = True
            addToCrashAndBugReport(
                f"BUG FOUND. This characteristic of handle 0x{attribute.handle:04X} does not have READ permission\n"
            )

        return value
    except ProtocolError as error:
        print(
            color(f"[!]  Cannot read attribute 0x{attribute.handle:04X}:", "yellow"),
            error,
        )
        # if split[0][0] == "S" and PermissionsAct[handle][1].find("READ") != -1:
        #     print(
        #         color(
        #             f"BUG FOUND. This service of handle 0x{attribute.handle:04X} has READ permission, but is not being READ\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. This service of handle 0x{attribute.handle:04X} has READ permission, but is not being READ\n"
        #     )

        # elif split[0][0] == "D" and PermissionsAct[handle][1].find("READ") != -1:
        #     print(
        #         color(
        #             f"BUG FOUND. This descriptor of handle 0x{attribute.handle:04X} has READ permission, but is not being READ\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. This descriptor of handle 0x{attribute.handle:04X} has READ permission, but is not being READ\n"
        #     )

        # if split[0][0] == "C" and PermissionsAct[handle][1].find("READ") != -1:
        #     print(
        #         color(
        #             f"BUG FOUND. This characteristic of handle 0x{attribute.handle:04X} has READ permission, but is not being READ\n",
        #             "red",
        #         )
        #     )
        #     result_dict["bug_present"] = True
        #     addToCrashAndBugReport(
        #         f"BUG FOUND. This characteristic of handle 0x{attribute.handle:04X} has READ permission, but is not being READ\n"
        #     )

    except TimeoutError:
        print(color("[!] Read Timeout"))
        addToCrashAndBugReport(
            f"bumble.core.TimeoutError for 0x{attribute.handle:04X}. Zephyr may have crashed.\n"
        )
        zephyr_died()
        if zephyr_died == False:
            kill_all_zephyr_processes()
        zephyr_died()

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
        PermissionsAct = {}
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

        # -------- Main interaction with the target here --------
        print("=== No Read/Write Attributes (Handles)")

        for attribute in attributes:
            str_attribute = str(attribute)
            split = str_attribute.split(",")
            if split[0][0] == "S":
                PermissionsAct[split[0][15:]] = ["Service", "READ"]
            elif split[0][0] == "D":
                PermissionsAct[split[0][18:]] = ["Descriptor", "READ"]
            elif split[0][0] == "C":
                PermissionsAct[split[0][22:]] = ["Characteristic", split[-1][1:-1]]
            await write_target(target, attribute, self.t_prime, PermissionsAct)
            if zephyr_died == True:
                break
            await read_target(target, attribute, PermissionsAct)
            if zephyr_died == True:
                break

        print("---------------------------------------------------------------")
        print(color("[OK] Communication Finished", "green"))
        print("---------------------------------------------------------------")
        # ---------------------------------------------------
        self.communicationOver = True


# Find pid of zephyr.exe


def find_pid(process_name):
    """Finds the PID for the given process name."""
    for proc in psutil.process_iter(["pid", "name"]):
        if process_name in proc.info["name"]:
            return proc.pid
    return None


# def zephyr_died():
#     zephyr_pid = find_pid("zephyr.exe")

#     # Kill the process with the obtained pid
#     if zephyr_pid:
#         print("Zephyr still alive")
#         return False
#     else:
#         print("Zephyr died")
#         return True


def zephyr_died():
    """
    Check if the specific zephyr process with the given command line arguments has died.

    Returns:
    bool: True if the process is not found (i.e., it has died), False otherwise (still running).
    """
    target_process_name = "zephyr.exe"
    target_arguments = ["--bt-dev=127.0.0.1:9000"]

    # Iterate over all processes to find a matching process
    for process in psutil.process_iter(["name", "cmdline"]):
        try:
            # Extract the process name and command line arguments
            if process.info["name"] == target_process_name:
                # Check if all target arguments are present in the process's command line
                if all(arg in process.info["cmdline"] for arg in target_arguments):
                    print("Zephyr still alive")
                    return False  # Process is found and thus alive
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process has terminated or we do not have permission to access its info
            continue

    print("Zephyr died")
    return True


def wait_for_process_to_die(pid, timeout=10):
    """Waits for the process with the given pid to terminate."""
    try:
        process = psutil.Process(pid)
        process.terminate()  # Sends SIGTERM
        process.wait(timeout=timeout)  # Waits for the process to terminate
        print(f"Process {pid} has been terminated.")
    except psutil.NoSuchProcess:
        print(f"No such process with pid {pid} to terminate.")
    except psutil.TimeoutExpired:
        print(f"Process {pid} did not terminate in {timeout} seconds.")
        process.kill()  # Sends SIGKILL as a last resort
        print(f"Process {pid} has been killed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def kill_zephyr():
    zephyr_pid = find_pid("zephyr.exe")
    if zephyr_pid:
        print("Attempting to terminate zephyr.exe")
        wait_for_process_to_die(zephyr_pid)


def kill_all_zephyr_processes():
    print("Killing zephyr")
    process_killed = False
    for process in psutil.process_iter(["name", "pid"]):
        if process.info["name"] == "zephyr.exe":
            pid = process.info["pid"]
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=5)
                logging.info(f"Successfully terminated 'zephyr.exe' with PID {pid}.")
                process_killed = True
            except psutil.NoSuchProcess:
                logging.warning(f"No such process with PID {pid}.")
            except psutil.TimeoutExpired:
                logging.error(
                    f"Timeout expired: 'zephyr.exe' with PID {pid} did not terminate, attempting SIGKILL."
                )
                proc.kill()
            except Exception as e:
                logging.error(f"Error killing 'zephyr.exe' with PID {pid}: {str(e)}")
    if not process_killed:
        result_dict["crash"] = True
        logging.info("No 'zephyr.exe' processes were found to kill.")
    else:
        result_dict["crash"] = False


def get_lcov():

    # Capture and summarize code coverage using lcov after confirming the process is dead
    fileName = "lcov_" + str(time.time_ns()) + ".info"
    result_dict["lcovFilename"] = fileName
    fullDir = os.path.join("lcov_coverage", fileName)
    lcov_capture_command = f"lcov --capture --directory ./ --output-file {fullDir} -q --rc lcov_branch_coverage=1"
    os.system(lcov_capture_command)

    lcov_summary_command = f"lcov --rc lcov_branch_coverage=1 --summary {fullDir}"
    os.system(lcov_summary_command)


def delete_file(file_path):
    """Delete a file if it exists."""
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")


def find_gcda_files():
    """Search for .gcda files within the specified directory and its subdirectories."""
    # This constructs a path pattern to search for .gcda files.
    directory = "~/STV-Project/BLE"
    path_pattern = os.path.join(directory, "**", "*.gcda")

    # The glob.glob function with recursive=True allows searching this pattern in all subdirectories.
    gcda_files = glob.glob(path_pattern, recursive=True)

    # Check if we found any files and print the result.
    if gcda_files:
        print(f"Found .gcda files:")
        for file in gcda_files:
            print(file)
    else:
        print("No .gcda files found.")


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


def read_t_prime():
    with open("t_prime.txt", "r") as file:
        hex_string = file.read().strip()  # Strip any leading/trailing whitespace
    byte_values = [int(hex_string[i : i + 2], 16) for i in range(0, len(hex_string), 2)]
    return byte_values


def write_result(t_prime, bug=False):
    filename = "result.json"
    delete_file(filename)
    print("Writing to result.json...")
    with open(filename, "w") as file:
        json.dump(result_dict, file, indent=4)


def is_process_alive(process_name, arguments):
    """
    Check if there is any running process that matches the process_name and includes all specified arguments.

    Args:
    - process_name (str): The name of the process to check for.
    - arguments (list of str): A list of arguments that must all be present in the process's command line.

    Returns:
    - bool: True if such a process is found, False otherwise.
    """
    # Iterate over all processes
    for process in psutil.process_iter(["name", "cmdline"]):
        try:
            # Check if process name matches and all specified arguments are in the command line
            if process.info["name"] == process_name and all(
                arg in process.info["cmdline"] for arg in arguments
            ):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process has been terminated or we don't have permission to access its info
            continue
    return False


# -----------------------------------------------------------------------------
async def main():

    print(">>> Waiting connection to HCI...")
    tcp_server = "tcp-server:127.0.0.1:9000"
    async with await open_transport_or_link(tcp_server) as (hci_source, hci_sink):
        print(">>> Connected")
        delete_gcda_files()
        find_gcda_files()

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
        t_prime = read_t_prime()
        print("t_prime : ", t_prime)
        device.listener = TargetEventsListener(t_prime)

        # Start BLE scanning here
        await device.power_on()
        await device.start_scanning()  # this calls "on_advertisement"
        with open("scan_signal.txt", "w") as signal_file:
            signal_file.write("scanning")
        print("Scanning started and signal file created.")

        print("Waiting Advertisment from BLE Target")
        while device.listener.got_advertisement is False:
            await asyncio.sleep(0.5)
        await device.stop_scanning()  # Stop scanning for targets

        print(color("\n[OK] Got Advertisment from BLE Target!", "green"))
        target_address = device.listener.advertisement.address

        # Start BLE connection here
        print(f"=== Connecting to {target_address}...")
        await device.connect(target_address)  # this calls "on_connection"

        # Wait in an infinite loop
        # await hci_source.wait_for_termination()
        while not device.listener.communicationOver:
            await asyncio.sleep(0.5)

        print("Communication is over")

        delete_file("scan_signal.txt")

        kill_all_zephyr_processes()

        get_lcov()
        write_result(t_prime)
        # want to wait for30s before closing
        await asyncio.sleep(10)
        kill9000()


# -----------------------------------------------------------------------------
logging.basicConfig(level=os.environ.get("BUMBLE_LOGLEVEL", "INFO").upper())
asyncio.run(main())
