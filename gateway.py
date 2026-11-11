import threading
import struct
import can
import cantools
import logging
import sys
from systemd.journal import JournalHandler
from time import sleep

# Setup logging
log = logging.getLogger('dashboard')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

db = cantools.database.load_file('HP_Dominator_V6.dbc')
