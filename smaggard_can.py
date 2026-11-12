import struct
from typing import List

# A map of the Holley CAN IDS to their names for human readability
TCUGear = 0x1E4FD000 # CAN INPUT 22
parkingFlag = 0x1E52D000 # CAN INPUT 34
fuelLevel = 0x1E202001 # CAN ID 1, input 1
acKick = 0x1E206001 # CAN ID 1 input 2
acHighSidePressure = 0x1E20A001 # CAN ID 1 input 3
reducedPower = 0x1E20E001 # CAN ID 1 input 4
outsideAir = 0x1E212001 # CAN ID 1 input 5

# A map of the GM CAN IDS to their names for human readability
Engine_General_Status_5 = 0x4D1
Engine_General_Status_2 = 0x3D1
Engine_General_Status_3 = 0x3F9
OutSideAirTemp = 0x3F1
Transmission_General_Status_2 = 0x1F5

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
  try:
    hexarray = [f"0x{b:02x}" for b in struct.pack(">f", val)]
    return [int(x, 16) for x in hexarray]
  except Exception as e:
    print(e)

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

def create_hex_list(data: bytearray) -> List:
  """ Converts an incoming CAN message into a hex list

      Args:
        data (bytearray):  the msg.data object to convert

      Returns:
        List: A hex value list of the bytearray
  """
  hex_list = [f"0x{b:02x}" for b in data]
  return hex_list

def read_gear(value: int, park_flag: bool) -> List:
  """ Takes the current gear value and park_flag values as integers and returns
      a list that would be sent to the GM E38 ECU/BCM module to let it know
      what gear the transmission is currently in.

      Args:
        value (int): Current gear value.
        park_flag (bool): Current Park Flag

      Returns:
        List: 8 length list depicting the current selected gear as the GM ECM/BCM
              expects to see.
  """
  # Create an list of 0's
  gear_list = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  # Match on value
  match value:
    # Neutral/Park
    case 0:
      # Park
      if park_flag: # Neutral
        gear_list[0] = 0x0F
        gear_list[1] = 0x0F
        gear_list[3] = 0x01
      # Neutral
      elif not park_flag:
        gear_list[0] = 0x0D
        gear_list[1] = 0x0D
        gear_list[3] = 0x03
    # Reverse
    case -1:
      gear_list[0] = 0x0E
      gear_list[1] = 0x0E
      gear_list[3] = 0x02
      gear_list[6] = 0x02
    # In Gear
    case x if x > 0:
      gear_list[0] = hex(x)
      gear_list[1] = hex(x)
      gear_list[3] = 0x04
      gear_list[6] = 0x03
  # Return the list.
  return gear_list



if __name__ == "__main__":
  # Add test code here.
  print("blah")
