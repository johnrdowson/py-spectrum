from enum import IntEnum
from dataclasses import dataclass


def attr_name_to_id(attr_name: str) -> int:
    """
    Attempts to lookup the attribute ID (hex) from the name. If no match is
    found, the name is assumed to be a hexadecimal (as string), and is therefore
    returned as an integer type. Otherwise, the lookup fails.
    """
    try:
        return SpectrumModelAttributes[attr_name.upper()].value
    except KeyError:
        try:
            return int(str(attr_name), 0)
        except ValueError:
            raise ValueError(
                f"'{attr_name}' is not a recognised Spectrum attribute name or "
                f"valid ID."
            )


def attr_id_to_name(attr_id: int) -> str:
    """
    Attempts to match the attribute ID to the corresponding name. If no match
    found, the ID is returned as a hexadecimal in string format.
    """
    try:
        return SpectrumModelAttributes(int(attr_id, 0)).name.lower()
    except ValueError:
        return hex(int(attr_id, 0))


@dataclass
class SpectrumModelAttributes(IntEnum):
    """ Attribute name to ID mappings """

    MODEL_HANDLE = 0x129FA
    MODEL_NAME = 0x1006E
    MODEL_TYPE_HANDLE = 0x10001
    MODEL_TYPE_NAME = 0x10000
    NETWORK_ADDRESS = 0x12D7F
    MANUFACTURER = 0x10032
    SERIAL_NUMBER = 0x10030
    SYS_LOCATION = 0x1102E
    SYS_DESC = 0x10052
    DEVICE_TYPE = 0x23000E
    CONDITION = 0x1000A
    TOPOLOGY_MODEL_NAME_STRING = 0x129E7
    COLLECTIONS_MODEL_NAME_STRING = 0x12ABD
    IS_MANAGED = 0x1295D

    def __str__(self) -> str:
        return hex(self.value)