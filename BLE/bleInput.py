from targetInput import TargetInput
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


class BLE_ReadATT_Input(TargetInput):
    def __init__(self, attribute):
        self.attribute = attribute

    def __str__(self):
        return f"""BLE_ReadATT_Input (attributeHandle = {self.attribute.handle})"""

    def getNumOfFuzzableInputs(self):
        return 1


class BLE_WriteATT_Input(TargetInput):
    def __init__(self, attribute, writeInput):
        self.attribute = attribute
        self.writeInput = writeInput

    def __str__(self):
        return f"""
        BLE_WriteATT_Input(
        attributeHandle = {self.attribute.handle}
        writeInput = {self.writeInput}) """

    def getNumOfFuzzableInputs(self):
        return 2
