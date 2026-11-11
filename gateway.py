import threading
import struct
import can
import cantools
import logging
import sys
from systemd.journal import JournalHandler
from time import sleep

# Setup logging
log = logging.getLogger('can-gateway')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

holley_db = cantools.database.load_file('HP & Dominator V6.dbc')
gmlan_db = cantools.database.load_file('GM HS-LAN.dbc')

holley_filters = [
  {"can_mask": 0xFFFFF800, "extended": True}
]

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')
can1 = can.interface.Bus(channel = 'can1', bustype = 'socketcan', can_filters = holley_filters)

