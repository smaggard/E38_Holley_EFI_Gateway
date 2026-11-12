import threading
import struct
import can
import cantools
import logging
import sys
from systemd.journal import JournalHandler
from time import sleep
from typing import List

# Setup logging
log = logging.getLogger('can-gateway')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

holley_db = cantools.database.load_file('HP & Dominator V6.dbc')
gmlan_db = cantools.database.load_file('GM HS-LAN.dbc')

holley_target_ids = [Holley_IDS]
gm_target_ids = [0x4D1, 0x3D1, 0x3F9, 0x3F1]

gm_filters = [
  {"can_id": msg_id, "can_mask": 0x7FF, "extended": False}
  for msg_id in gm_target_ids
]

holley_filters = [
  {"can_id": msg_id, "can_mask": 0xFFFFF800, "extended": True}
  for msg_id in holley_target_ids
]

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', can_filters = gm_filters)
can1 = can.interface.Bus(channel = 'can1', bustype = 'socketcan', can_filters = holley_filters)

# Convert Float to Hex list.
def float_to_array(val: float) -> List:
  hexarray = [f"0x{b:02x}" for b in struct.pack(">f", val)]
  return hexarray

# Convert Hex to Floating point.
def hex_to_float(f: str) -> float:
    return struct.unpack('!f',bytes.fromhex(f))[0]

def holley_can_listener() -> None:
  # to do

def gm_can_listener() -> None:
  #to do

if __name__ == "__main__":
    try:
        holley_can_thread = threading.Thread(target=holley_can_listener)
        gm_can_thread = threading.Thread(target=gm_can_listener)
        holley_can_thread.start()
        gm_can_thread.start()
        holley_can_thread.join()
        gm_can_thread.join()
    except KeyboardInterrupt as e:
        sys.exit(1)
