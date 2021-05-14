from enum import IntEnum


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


class SpectrumModelAttributes(IntEnum):
    """ Attribute name to ID mappings """

    COLLECTIONS_MODEL_NAME_STRING = 0x12ADB
    CONDITION = 0x1000A
    DEVICE_TYPE = 0x23000E
    IS_MANAGED = 0x1295D
    LAST_SUCCESSFUL_POLL = 0x11620
    MANUFACTURER = 0x10032
    MDL_CREAT_TIME = 0x1102A
    MODEL_CLASS = 0x11EE8
    MODEL_HANDLE = 0x129FA
    MODEL_NAME = 0x1006E
    MODEL_TYPE_HANDLE = 0x10001
    MODEL_TYPE_NAME = 0x10000
    NCM_DEVICE_FAMILY_INDEX = 0x12BEF
    NCM_POTENTIAL_COMM_MODES = 0x12BEB
    NCM_SELECTED_COMM_MODE = 0x12BEC
    NETWORK_ADDRESS = 0x12D7F
    SERIAL_NUMBER = 0x10030
    SYS_DESC = 0x10052
    SYS_LOCATION = 0x1102E
    TOPOLOGY_MODEL_NAME_STRING = 0x129E7

    def __str__(self) -> str:
        return hex(self.value)

    def __repr__(self) -> str:
        return f"{str(self.name).lower()}: {hex(self.value)}"
