#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
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
from ble_fuzzer import BLE_Fuzzer


# -----------------------------------------------------------------------------
class TargetEventsListener(Device.Listener):

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
        bleFuzzer = BLE_Fuzzer(target, attributes)
        await bleFuzzer.fuzz()

        print("---------------------------------------------------------------")
        print(color("[OK] Communication Finished", "green"))
        print("---------------------------------------------------------------")
        # ---------------------------------------------------


# -----------------------------------------------------------------------------
async def main():
    if len(sys.argv) != 2:
        print("Usage: run_controller.py <transport-address>")
        print("example: ./run_ble_tester.py tcp-server:0.0.0.0:9000")
        return

    print(">>> Waiting connection to HCI...")
    async with await open_transport_or_link(sys.argv[1]) as (hci_source, hci_sink):
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
        await device.start_scanning()  # this calls "on_advertisement"  #scanning state

        print("Waiting Advertisment from BLE Target")
        while device.listener.got_advertisement is False:
            await asyncio.sleep(0.5)
        await device.stop_scanning()  # Stop scanning for targets

        print(color("\n[OK] Got Advertisment from BLE Target!", "green"))
        target_address = device.listener.advertisement.address

        # Start BLE connection here
        print(f"=== Connecting to {target_address}...")
        await device.connect(
            target_address
        )  # this calls "on_connection"   #send these requests: version, feature, length,MTU length --> get supported LL features and capabilities such as max length of packet it can send/receive
        #

        # Wait in an infinite loop
        await hci_source.wait_for_termination()


# -----------------------------------------------------------------------------
logging.basicConfig(level=os.environ.get("BUMBLE_LOGLEVEL", "INFO").upper())
asyncio.run(main())
