import struct
from typing import List

# A map of the Holley CAN IDS to their names for human readability
holley_id_map = {
  "TCU Gear": 0x1E4FD000, # CAN INPUT 22
  "Parking Flag": 0x1E52D00, # CAN INPUT 34
  "fuelLevel": 0x1E202001, # CAN ID 1, input 1
  "acKick": 0x1E206001, # CAN ID 1 input 2
  "acHighSidePressure": 0x1E20A001, # CAN ID 1 input 3
  "reducedPower": 0x1E20E001, # CAN ID 1 input 4
  "outsideAir": 0x1E212001, # CAN ID 1 input 5
}

# A map of the GM CAN IDS to their names for human readability
gm_id_map = {
  "Engine_General_Status_5": 0x4D1,
  "Engine_General_Status_2": 0x3D1,
  "Engine_General_Status_3": 0x3F9,
  "OutSideAirTemp": 0x3F1,
  "Transmission_General_Status_2": 0x1F5
}

# List of IDS to filter on the Holley side.
holley_target_ids = [0x1E4FD000, 0x1E52D000]

# List of IDS to filter on the GMLAN side.
gm_target_ids = [0x4D1, 0x3D1, 0x3F9, 0x3F1]

# Convert Float to Hex list.
def float_to_array(val: float) -> List:
  """ Create a Hex List from a float so it can be sent as a Holley EFI CAN message.

      Args:
        val (float): Reading as a float

      Returns:
        List: A list of the hex values that represent the float.
  """
  hexarray = [f"0x{b:02x}" for b in struct.pack(">f", val)]
  return hexarray

# Convert Hex to Floating point.
def hex_to_float(f: str) -> float:
    """ Create a float from an incoming Holley EFI Hex List the float can then be used.
        The list first needs to be converted to a raw string.

        Example: 
          raw_bytes = str(msg.data.hex())[:8]
          value = hex_to_float(raw_bytes)

        Args:
          f (str): Hex array as a string
          
        Returns:
          float: A float reprentation of the hex array.
  """
    return struct.unpack('!f',bytes.fromhex(f))[0]

def bit_read(x: int, n: int) -> int:
  """ Pulls a bit from a int at a certain position.

      Args:
        x (int): Value to pull the bit from.
        n (int): Position of bit to return starting from rightmost.

      Returns:
        int: Value of bit in [0,1] of the bit location requested.
  """
  return (x >> n) & 1


if __name__ == "__main__":
  # Add test code here.
  print("blah")
