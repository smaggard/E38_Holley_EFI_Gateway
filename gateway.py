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
  {"can_id": msg_id, "can_mask": 0x1FFFF800, "extended": True}
  for msg_id in smaggard_can.holley_target_ids
]
print(holley_filters)

can0 = can.Bus(channel = 'can0', interface = 'socketcan', can_filters = gm_filters)
can1 = can.Bus(channel = 'can1', interface = 'socketcan', can_filters = holley_filters)

def holley_can_listener() -> None:
  # Define Park, always assume park on first run
  park_flag = 1.0
  try:
    log.info("Starting CAN Interface")
    with can1 as Bus:
      for msg in Bus:
        msg_id = msg.arbitration_id & 0x1FFFF800
        raw_bytes = str(msg.data.hex())[:8]
        if len(raw_bytes) == 8:
          value = round(smaggard_can.hex_to_float(raw_bytes),2)
          match msg_id:
            case 0x1E52D000:
              park_flag = value
              print(park_flag)
            case 0x1E4FD000:
              can_data = smaggard_can.read_gear(int(value), bool(park_flag))
              msg = can.Message(arbitration_id=0x1F5, data=can_data, is_extended_id=False)
              try:
                can0.send(msg)
                print("Sent message to GM")
              except can.CanError as e:
                print(f"Message not sent: {e}")
              print(can_data)
            case _:
              continue
        else:
          continue
            
  except Exception as e:
    log.error(e)
    print(e)
        
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
