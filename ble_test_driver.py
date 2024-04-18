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
import hashlib

from bumble.device import Device, Peer
from bumble.host import Host
from bumble.gatt import show_services
from bumble.core import ProtocolError
from bumble.controller import Controller
from bumble.link import LocalLink
from bumble.transport import open_transport_or_link
from bumble.utils import AsyncRunner
from bumble.colors import color
#from bleFuzzer import BLE_Fuzzer

import random

async def write_target(target, attribute, bytes):
    # Write
    
    try:
        bytes_to_write = bytearray(bytes)
        await target.write_value(attribute, bytes_to_write, True)
        print(attribute)
        print(color(f'[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}', 'green'))
        
        return True
    except ProtocolError as error:
        print(color(f'[!]  Cannot write attribute 0x{attribute.handle:04X}:', 'yellow'), error)
    except TimeoutError:
        print(color('[X] Write Timeout', 'red'))
        
    return False


async def read_target(target, attribute):
    # Read
    try: 
        read = await target.read_value(attribute)
        value = read.decode('latin-1')
        print(color(f'[OK] READ  Handle 0x{attribute.handle:04X} <-- Bytes={len(read):02d}, Val={read.hex()}', 'cyan'))
        return value
    except ProtocolError as error:
        print(color(f'[!]  Cannot read attribute 0x{attribute.handle:04X}:', 'yellow'), error)
    except TimeoutError:
        print(color('[!] Read Timeout'))
    
    return None

# -----------------------------------------------------------------------------
class TargetEventsListener(Device.Listener):

    got_advertisement = False
    advertisement = None
    connection = None
        
    def on_advertisement(self, advertisement):

        print(f'{color("Advertisement", "cyan")} <-- '
              f'{color(advertisement.address, "yellow")}')
        
        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True


    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        print(color(f'[OK] Connected!', 'green'))
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        print('=== Discovering services')
        target = Peer(connection)
        attributes = []

        PermissionsRun = {}
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

        print(color('[OK] Services discovered', 'green'))
        show_services(target.services)
        
        # -------- Main interaction with the target here --------
        print('=== Read/Write Attributes (Handles)')
        print(attributes[5])
        for attribute in attributes:
            str_attribute = str(attribute)
            split = str_attribute.split(',')
            if split[0][0] == 'S':
                PermissionsAct[split[0][15:]] = ['Service', 'READ']
            elif split[0][0] == 'D':
                PermissionsAct[split[0][18:]] = ['Descriptor', 'READ']
            elif split[0][0] == 'C':
                PermissionsAct[split[0][22:]] = ['Characteristic', split[-1][1:-1]]            
            await write_target(target, attribute, [0x0FF])
            await read_target(target, attribute)
        print(PermissionsAct)

        #current_time = int(time.time())
        #random.seed(current_time)
        #bleFuzzer = BLE_Fuzzer(target, attributes)

        #await bleFuzzer.fuzz()
        
        print('---------------------------------------------------------------')
        print(color('[OK] Communication Finished', 'green'))
        print('---------------------------------------------------------------')

        def calculate_hash(filename, linenumber):
            return hashlib.sha256(f"{filename}-{linenumber}".encode()).hexdigest()

        file_path = ""
        hit_counts = {}

        with open('lcov.info', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('SF:'):
                    file_path = line.split(':', 1)[1]
                elif line.startswith('DA:'):
                    parts = line.split(',')
                    print(parts)
                    line_number = parts[0]
                    hit_count = int(parts[1])
                    file_hash = calculate_hash(file_path, line_number)
                    hit_counts[file_hash] = hit_count

        print(hit_counts)
        # ---------------------------------------------------
        
        

# -----------------------------------------------------------------------------
async def main():
    if len(sys.argv) != 2:
        print('Usage: run_controller.py <transport-address>')
        print('example: ./run_ble_tester.py tcp-server:0.0.0.0:9000')
        return

    print('>>> Waiting connection to HCI...')
    async with await open_transport_or_link(sys.argv[1]) as (hci_source, hci_sink):
        print('>>> Connected')

        # Create a local communication channel between multiple controllers
        link = LocalLink()

        # Create a first controller for connection with host interface (Zephyr)
        zephyr_controller = Controller('Zephyr', host_source=hci_source,
                                 host_sink=hci_sink, link=link)


        # Create our own device (tester central) to manage the host BLE stack
        device = Device.from_config_file('tester_config.json')
        # Create a host for the second controller
        device.host = Host() 
        # Create a second controller for connection with this test driver (Bumble)
        device.host.controller = Controller('Fuzzer', link=link)
        # Connect class to receive events during communication with target
        device.listener = TargetEventsListener()
        
        # Start BLE scanning here
        await device.power_on()
        await device.start_scanning() # this calls "on_advertisement"

        print('Waiting Advertisment from BLE Target')
        while device.listener.got_advertisement is False:
            await asyncio.sleep(0.5)
        await device.stop_scanning() # Stop scanning for targets

        print(color('\n[OK] Got Advertisment from BLE Target!', 'green'))
        target_address = device.listener.advertisement.address

        # Start BLE connection here
        print(f'=== Connecting to {target_address}...')
        await device.connect(target_address) # this calls "on_connection"
        
        # Wait in an infinite loop
        await hci_source.wait_for_termination()


# -----------------------------------------------------------------------------
logging.basicConfig(level=os.environ.get('BUMBLE_LOGLEVEL', 'INFO').upper())
asyncio.run(main())
