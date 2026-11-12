import threading
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

can0 = can.Bus(channel = 'can0', interface = 'socketcan', can_filters = gm_filters)
can1 = can.Bus(channel = 'can1', interface = 'socketcan', can_filters = holley_filters)

def holley_can_listener() -> None:
  # Define Park, always assume park on first run
  park_flag = 1.0
  try:
    log.info("Starting Holley CAN Interface")
    with can1 as Bus:
      for msg in Bus:
        msg_id = msg.arbitration_id & 0x1FFFF800
        raw_bytes = str(msg.data.hex())[:8]
        if len(raw_bytes) == 8:
          value = round(smaggard_can.hex_to_float(raw_bytes),2)
          match msg_id:
            case smaggard_can.parkingFlag:
              park_flag = value
            case smaggard_can.TCUGear:
              can_data = smaggard_can.read_gear(int(value), bool(park_flag))
              log.error(can_data)
              msg = can.Message(arbitration_id=smaggard_can.Transmission_General_Status_2,
                                data=can_data, is_extended_id=False)
              try:
                can0.send(msg)
              except can.CanError as e:
                log.error(f"Message not sent: {e}")
            case _:
              continue
        else:
          continue

  except Exception as e:
    log.error(e)

def gm_can_listener() -> None:
  try:
    log.info("Starting GM CAN Interface")
    with can0 as Bus:
      for msg in Bus:
        msg_id = msg.arbitration_id & 0x7FF

        data = smaggard_can.create_hex_list(msg.data)
        match msg_id:
          case smaggard_can.Engine_General_Status_5:
            try:
              fuelLevel = int(data[5], 16) * 0.392157
            except Exception as e:
              log.error(e)
            try:
              reducedPower = smaggard_can.bit_read(int(data[3], 16), 7)
            except Exception as e:
              log.error(e)
            try:
              fl_msg = can.Message(arbitration_id=smaggard_can.fuelLevel,
                                   data=smaggard_can.float_to_array(fuelLevel),
                                   is_extended_id=True)
              rp_msg = can.Message(arbitration_id=smaggard_can.reducedPower,
                                   data=smaggard_can.float_to_array(reducedPower),
                                   is_extended_id=True)
            except Exception as e:
              log.error(e)
            try:
              can1.send(fl_msg)
              can1.send(rp_msg)
            except can.CanError as e:
                log.error(e)
          case smaggard_can.Engine_General_Status_2:
            try:
              acKick = smaggard_can.bit_read(int(data[4], 16), 5)
            except Exception as e:
              log.error(e)
            try:
              ak_msg = can.Message(arbitration_id=smaggard_can.acKick,
                                   data=smaggard_can.float_to_array(acKick),
                                   is_extended_id=True)
            except Exception as e:
              log.error(e)
            try:
              can1.send(ak_msg)
            except can.CanError as e:
              log.error(e)
          case smaggard_can.Engine_General_Status_3:
            try:
              acHighSide = (int(data[7], 16) * 14) / 6.895
            except Exception as e:
              log.error(e)
            try:
              ac_msg = can.Message(arbitration_id=smaggard_can.acHighSidePressure,
                                   data=smaggard_can.float_to_array(acHighSide),
                                   is_extended_id=True)
            except Exception as e:
              log.error(e)
            try:
              can1.send(ac_msg)
            except can.CanError as e:
              log.error(e)
          case smaggard_can.OutSideAirTemp:
            try:
              outsideAir = ((((int(data[7], 16) * .5) -40) * 1.8) +32)
            except Exception as e:
              log.error(e)
            try:
              oa_msg = can.Message(arbitration_id=smaggard_can.outsideAir,
                                   data=smaggard_can.float_to_array(outsideAir),
                                   is_extended_id=True)
            except Exception as e:
              log.error(e)
            try:
              can1.send(oa_msg)
            except can.CanError as e:
              log.error(e)
          case _:
            continue
  except Exception as e:
      log.error(e)


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
