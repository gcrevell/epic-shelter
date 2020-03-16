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

SELFTEST_LEVEL_DATABASE_READABLE = '-v0'
SELFTEST_LEVEL_DATABASE_INTEGRITY = '-v1'
SELFTEST_LEVEL_DATABASE_CONTENT = '-v2'
SELFTEST_LEVEL_LOCAL_ARCHIVES = '-v3'
SELFTEST_LEVEL_LOCAL_REMOTE_ARCHIVES = '-v4'
SELFTEST_LEVEL_FILE_RESTORE = '-v5'

SELFTEST_INCREMENTAL_SPAN_MONTH = '1d/30d'
SELFTEST_INCREMENTAL_SPAN_YEAR = '1d/365d'

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

# Selftest methods

# Log methods

def get_media_backup_logs():
    """
    Get HashBackup logs for the media backups

    Returns:
        string -- The output of the HashBackup log command
    """
    return get_backup_logs(MEDIA_BACKUP_DIR)

def get_plex_db_backup_logs():
    """
    Get HashBackup logs for the database backups

    Returns:
        string -- The output of the HashBackup log command
    """
    return get_backup_logs(PLEX_DB_BACKUP_DIR)

def get_backup_logs(backup_dir):
    """
    Get HashBackup logs for the defined backup directory

    Arguments:
        backup_dir {string} -- The backup directory path to get the logs for

    Returns:
        string -- The output of the HashBackup log command
    """
    return subprocess.run([HB_EXECUTABLE, 'log', '-c', backup_dir, '-s', '-d7', '-x2'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8")

# Stats methods

def get_media_backup_stats():
    """
    Get backup stats for the media files
    
    Returns:
        string -- The backup stats
    """
    return get_backup_stats(MEDIA_BACKUP_DIR)

def get_plex_db_backup_stats():
    """
    Get backup stats for the Plex DB backup
    
    Returns:
        string -- The backup stats
    """
    return get_backup_stats(PLEX_DB_BACKUP_DIR)

def get_backup_stats(backup_dir):
    """
    Get the backup stats for a given backup folder
    
    Arguments:
        backup_dir {string} -- The backup directory path to get the stats for
    
    Returns:
        string -- The stats of the backup directory
    """
    backup_stats = subprocess.run([HB_EXECUTABLE, 'stats', '-c', backup_dir], stdout=subprocess.PIPE).stdout.decode("utf-8")
    # Remove the first line (hashbackup info) and extra spaces
    stats_array = backup_stats.split("\n")[2:]
    stats_array_clean = []
    for stat in stats_array:
        stats_array_clean.append(stat.strip())
    
    return "\n".join(stats_array_clean)


def selftest_media_backup():
    run_selftest(MEDIA_BACKUP_DIR, SELFTEST_LEVEL_DATABASE_CONTENT, SELFTEST_INCREMENTAL_SPAN_YEAR)
    run_selftest(MEDIA_BACKUP_DIR, SELFTEST_LEVEL_LOCAL_REMOTE_ARCHIVES, SELFTEST_INCREMENTAL_SPAN_YEAR)

def selftest_plex_db_backup():
    run_selftest(PLEX_DB_BACKUP_DIR, SELFTEST_LEVEL_DATABASE_CONTENT, SELFTEST_INCREMENTAL_SPAN_MONTH)
    run_selftest(PLEX_DB_BACKUP_DIR, SELFTEST_LEVEL_LOCAL_REMOTE_ARCHIVES, SELFTEST_INCREMENTAL_SPAN_MONTH)

def run_selftest(backup_dir, check_level, incremental_span):
    return subprocess.run([HB_EXECUTABLE, 'selftest', '-c', backup_dir, check_level, '--inc', incremental_span]).returncode
