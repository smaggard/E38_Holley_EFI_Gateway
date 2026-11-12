import threading
import struct
import can
import cantools
import logging
import sys
from systemd.journal import JournalHandler
from time import sleep
from typing import List
import smaggard_can

# Setup logging
log = logging.getLogger('can-gateway')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

holley_db = cantools.database.load_file("HP & Dominator V6.dbc")
gmlan_db = cantools.database.load_file("GM HS-CAN.dbc")

gm_filters = [
  {"can_id": msg_id, "can_mask": 0x7FF, "extended": False}
  for msg_id in smaggard_can.gm_target_ids
]

holley_filters = [
  {"can_id": msg_id, "can_mask": 0xFFFFF800, "extended": True}
  for msg_id in smaggard_can.holley_target_ids
]

can0 = can.interface.Bus(channel = 'can0', interface = 'socketcan', can_filters = gm_filters)
can1 = can.interface.Bus(channel = 'can1', interface = 'socketcan', can_filters = holley_filters)

def holley_can_listener() -> None:
  # to do
  while 1:
    print("In Holley can")
    sleep(10)

def gm_can_listener() -> None:
  #to do
  while 1:
    print("In GM CAN")
    sleep(5)

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
