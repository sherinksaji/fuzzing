#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
import asyncio
import sys
import os
import time
import signal
from binascii import hexlify
import psutil
from bumble.device import Device, Peer
from bumble.host import Host
from bumble.gatt import show_services
from bumble.core import ProtocolError
from bumble.controller import Controller
from bumble.link import LocalLink
from bumble.transport import open_transport_or_link
from bumble.utils import AsyncRunner
from bumble.colors import color


async def write_target(target, attribute, bytes):
    # Write
    try:
        bytes_to_write = bytearray(bytes)
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
    except TimeoutError:
        print(color("[X] Write Timeout", "red"))

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
    def __init__(self):
        super().__init__()
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

        # -------- Main interaction with the target here --------
        print("=== No Read/Write Attributes (Handles)")

        for attribute in attributes:
            await write_target(target, attribute, [0x01])
            await read_target(target, attribute)

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


def zephyr_died():
    zephyr_pid = find_pid("zephyr.exe")

    # Kill the process with the obtained pid
    if zephyr_pid:
        print("Zephyr still alive")
        return False
    else:
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


def get_lcov():
    zephyr_pid = find_pid("zephyr.exe")
    if zephyr_pid:
        print("Attempting to terminate zephyr.exe")
        wait_for_process_to_die(zephyr_pid)

    # Capture and summarize code coverage using lcov after confirming the process is dead
    fileName = "lcov_" + str(time.time_ns()) + ".info"
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


# -----------------------------------------------------------------------------
async def main():

    print(">>> Waiting connection to HCI...")
    tcp_server = "tcp-server:127.0.0.1:9000"
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
        device.listener = TargetEventsListener()

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
        get_lcov()

        delete_gcda_files()
        kill9000()


# -----------------------------------------------------------------------------
logging.basicConfig(level=os.environ.get("BUMBLE_LOGLEVEL", "INFO").upper())
asyncio.run(main())
