#!/opt/bin/python3

"""
This file contains some methods to turn uploading on or off
"""

import subprocess
from hb import MEDIA_BACKUP_DIR, PLEX_DB_BACKUP_DIR
from shutil import copy
from os import path

# Constants

# The file that has remote destinations on
DESTINATIONS_ON_FILE = 'dest.on.conf'

# The file that has remote destinations off
DESTINATIONS_OFF_FILE = 'dest.off.conf'

# The destinations file that is actually used
DESTINATIONS_FILE = 'dest.conf'

# Methods

def turn_on_destinations():
    set_destination_file(MEDIA_BACKUP_DIR, DESTINATIONS_ON_FILE)
    set_destination_file(PLEX_DB_BACKUP_DIR, DESTINATIONS_ON_FILE)

def turn_off_destinations():
    set_destination_file(MEDIA_BACKUP_DIR, DESTINATIONS_OFF_FILE)
    set_destination_file(PLEX_DB_BACKUP_DIR, DESTINATIONS_OFF_FILE)

def set_destination_file(directory, source_dest_file):
    """
    Given a backup directory, and an on or off dest file, copy it into the
    default dest file location to be used. Basically, turn destinations on or
    off for a given backup directory
    
    Arguments:
        directory {string} -- The backup directory
        source_dest_file {string} -- The source file. Should be `dest.on.conf`
        or `dest.off.conf`.
    """
    source_file_path = path.join(directory, source_dest_file)
    target_file_path = path.join(directory, DESTINATIONS_FILE)

    copy(source_file_path, target_file_path)
