#!/opt/bin/python3

import subprocess

HB_EXECUTABLE = '/share/Web/bin/hb'

def run_backup(backup_dir, files_dir):
    backup_output = subprocess.run([HB_EXECUTABLE, 'log', 'backup', '-c', backup_dir, files_dir])
