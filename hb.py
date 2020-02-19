#!/opt/bin/python3

"""
This contains the low level commands needed for running HashBackup commands.
"""

import subprocess

# Constants

# The hb executable location
HB_EXECUTABLE = '/share/Web/bin/hb'

# The media backup directory path
MEDIA_BACKUP_DIR = '/share/Backups/plex/media'

# The Plex database backup directory path
PLEX_DB_BACKUP_DIR = '/share/Backups/plex/db'

# The media directory path
MEDIA_DIR = '/share/Media/Videos'

# The plex database directory path
PLEX_DB_DIR = '/share/CACHEDEV2_DATA/.qpkg/PlexMediaServer/Library'

# Backup methods

def backup_media_file(file):
    """
    Backup a defined media file.

    Arguments:
        file {string} -- The path to the file to backup. Can also be a directory

    Returns:
        integer -- The return code of the `hb` command
    """
    return run_backup(MEDIA_BACKUP_DIR, file)

def backup_media():
    """
    Backup the whole videos directory.

    Returns:
        integer -- The return code of the `hb` command
    """
    return run_backup(MEDIA_BACKUP_DIR, MEDIA_DIR)

def backup_plex_db():
    """
    Backup the plex database.

    Returns:
        integer -- The return code of the `hb` command
    """
    return run_backup(PLEX_DB_BACKUP_DIR, PLEX_DB_DIR)

def run_backup(backup_dir, files_dir):
    """
    Backup the files with the `hb` backup command, and the defined backup directory.

    Arguments:
        backup_dir {string} -- The HashBackup destination directory
        files_dir {string} -- The directory or file to backup

    Returns:
        integer -- The return code of the `hb` command
    """
    return subprocess.run([HB_EXECUTABLE, 'log', 'backup', '-c', backup_dir, files_dir]).returncode
