#!/usr/bin/python
# Copyright (C) 2016 HashBackup, LLC.
#
# Example implementation of a shell destination that uses Rclone to
# copy files.  See http://rclone.org.  This script requires Python 2.7
#
# IMPORTANT: see the dest.conf.rclone example file for detailed
# information about options to this script.
#
# Shell destinations are used to connect to external storage not
# supported with a native destination, where sending, getting, and
# removing files can be done using a Unix command.
#
# Shell destinations report success or failure with their exit code.  If
# a non-zero exit code is returned (failure), the command is retried
# with exponential backoff like all other destinations.
#
# Example dest.conf for this shell destination:
#
#    destname acd
#    type shell
#    run python /test/hb/rclone.py --debug --args "-v --bwlimit 250K" --destname acd --backupdir /test/hb --clonedir acd:backups --command
#
# To make parsing easier, a --command option has been added to the
# end.  The command line is processed by the shell, so things like
# $PASSWORD, shell functions, and quoting work fine.
#
# HB adds a command and arguments to the end of the run command line.
# Below are the commands and the shell destination's responsibilities:
#
#   noop
#
#      exit 0; this is used once per worker during startup to ensure
#      the command is runnable
#
#   send pathname filename
#
#      send the local file indicated by pathname to the remote
#      destination and store it as filename.  Note that filename may
#      already exist on the remote, and HB expects send to overwrite
#      the existing file.  This happens for example with DESTID and
#      dest.db.  The file size may stay the same (always with DESTID),
#      so don't use file size as an indication of whether to copy a
#      file.  Ideally, the file should be unconditionally copied.
#
#      Some remote protocols like rsync, automatically prevent partial
#      files on the remote by copying first into a temp file, then
#      renaming the temp file to the real filename.  If your remote
#      protocol doesn't do this automatically (ftp doesn't for
#      example), it's a good idea, when possible, to send the file as
#      filename.tmp, then rename filename.tmp to filename, overwriting
#      filename if it already exists.  If the remote cannot rename
#      over an existing file, you can send as filename.tmp, delete
#      filename, then rename filename.tmp to filename.  This runs the
#      slight risk of a failure after the delete, which would have to
#      be corrected manually by renaming filename.tmp on the remote.
#      It will be corrected automatically on the next backup by
#      resending the file.
#
#   get pathname filename
#
#      fetch the remote file indicated by filename and store it in the
#      local file pathname.  If the file doesn't exist, return an error.
#
#   rm filename
#
#      remove the remote file indicated by filename.  If the file
#      doesn't exist, no error should occur.
#
# List of rclone exit codes:
#   0 = success
#   1 = Syntax or usage error
#   2 = Error not otherwise categorised
#   3 = Directory not found
#   4 = File not found
#   5 = Temporary error (one that more retries might fix) (Retry errors)
#   6 = Less serious errors (like 461 errors from dropbox) (NoRetry errors)
#   7 = Fatal error (one that more retries won't fix, like account suspended) (Fatal errors

from argparse import ArgumentParser
import errno
import os
import random
import re
from stat import *
import subprocess
import sys
import time

def runcmd(args):
    cmd = '/share/Web/rclone/rclone -I --stats=0'
    if opt.args:
        verb = False
        for a in opt.args.split():
            if a.startswith('-v') or a == '--verbose':
                verb = True
        if not verb:
            cmd += ' -q'
        cmd += ' ' + opt.args
    cmd += ' ' + args
    debug('Running command: %s' % cmd)
    rc = subprocess.call(cmd, shell=True)
    debug('Exit code %d for: %s' % (rc, cmd))
    return rc

def debug(msg):
    if opt.debug: print >>sys.stderr,  '%s[%d]: %s' % (opt.destname, os.getpid(), msg)

def warn(msg):
    print >>sys.stderr, '%s[%d]: %s' % (opt.destname, os.getpid(), msg)

# errors and warnings are the same for now

error = warn


warnedverify = False

def main(argv):
    global opt, warnedverify

    parser = ArgumentParser()
    parser.add_argument('--args', action="store", required=False)
    parser.add_argument('--verify', action="store_true", default=False)
    parser.add_argument('--debug', action="store_true", default=False)
    parser.add_argument('--destname', action='store', required=True)
    parser.add_argument('--backupdir', action='store', required=True)
    parser.add_argument('--clonedir', action='store', required=True)
    parser.add_argument('--command', action='store', required=True)
    parser.add_argument('arg', action='store', nargs='*')
    opt = parser.parse_args(argv)

    debug('received shell command: %s %s' % (opt.command, opt.arg))

    if opt.command == 'noop':
        if opt.verify and not warnedverify:
            warnedverify = True
            warn('%s: the --verify is not supported in this release and has been ignored' % opt.destname)
        try:
            statinfo = os.stat(opt.backupdir)
        except Exception, err:
            raise Exception, 'shell(%s): error reading --backupdir %s: %s' % (opt.destname, opt.backupdir, err)
        if not S_ISDIR(statinfo.st_mode):
            raise Exception, 'shell(%s): --backupdir is not a directory: %s' % (opt.destname, opt.backupdir)
        return 0

# --include doesn't cause an error if the file doeesn't exist (good),
# but causes remote directory listings (bad)
#
# delete (rclone 1.35) doesn't do remote directory listings (good),
# but causes errors and retries if the file isn't there (bad)
#
# Neither works right, so use delete, ignore errors, and assume they
# are "not found" errors.  This could lead to files being left on
# remotes but that seems to be the least bad result.

    if opt.command == 'rm':
#        rc = runcmd('--include %s delete %s' % (opt.arg[0], opt.clonedir))
        rc = runcmd('delete %s/%s' % (opt.clonedir, opt.arg[0]))
        return 0

    locpath = opt.arg[0]

    if opt.command == 'send':
        rc = runcmd('copyto %s %s/%s' % (locpath, opt.clonedir, opt.arg[1]))
        return rc

# rclone 1.35 creates empty directories if remote file doesn't exist;
# delete them if there before or after the get

    if opt.command == 'get':
        try:
            s = os.lstat(locpath)
        except OSError as (err, strerr):
            if err != errno.ENOENT:
                raise
        else:
            if S_ISDIR(s.st_mode):
                os.rmdir(locpath)
            else:
                os.remove(locpath)
        rc = runcmd('--no-gzip-encoding copyto %s/%s %s' % (opt.clonedir, opt.arg[1], locpath))
        try:
            s = os.lstat(locpath)
        except OSError as (err, strerr):
            if err == errno.ENOENT:
                debug('local file %s missing after get; returning exit code 1' % locpath)
                rc = 1
            else:
                raise
        else:
            if S_ISDIR(s.st_mode):
                os.rmdir(locpath)
                debug('rclone created empty directory for (missing?) remote file %s; returning exit code 1' % locpath)
                rc = 1
        return rc

# verify file is stored on remote and has the right size.
#
# Only return a verify error (return code 249) or file not found
# (return code 250) when we know the file is the wrong size or not
# there.  If there are other problems (rclone fails, the Python code
# fails, etc.), don't treat those like a verify error because it
# causes files to get re-uploaded.
#
# A .tmp file is used here because HB deletes them before every run.

    if opt.command == 'verify':
        vfyfilename = opt.arg[0]
        vfysize = opt.arg[1]
        lsoutpath = os.path.join(opt.backupdir, opt.destname + '.lsout.tmp')
        lsfd = None
        lsout = ''

# Apologies for the mess: one worker needs to do the directory ls, the
# others need to wait for it

        while lsout == '':
            try:
                lsfd = os.open(lsoutpath, os.O_RDONLY)
                lsout = os.read(lsfd, os.stat(lsoutpath).st_size)
            except OSError as (err, strerr):
                if err != errno.ENOENT:
                    error('error1 reading ls output from %s: %s' % (lsoutpath, strerr))
            except Exception, err:
                error('error2 reading ls output from %s: %s' % (lsoutpath, err))
            finally:
                if lsfd:
                    os.close(lsfd)
                    lsfd = None
            if lsout:
                break

# if ls not there, do a full directory list, but only in one worker

            try:
                lsfd = os.open(lsoutpath, os.O_WRONLY+os.O_TRUNC+os.O_CREAT+os.O_EXCL)
            except OSError as (err, strerr):
                if err != errno.EEXIST:
                    debug('error opening dir ls output file %s: %s' % (lsoutpath, strerr))
            except Exception, err:
                error('error opening dir ls output file %s: %s' % (lsoutpath, err))
            else:
                cmd = '/share/Web/rclone/rclone --stats=0 -q ls'
                cmdlist = cmd.split()
                cmdlist.append(opt.clonedir)
                debug('verify dir ls command: %s' % cmdlist)
                try:
                    lsout = subprocess.check_output(cmdlist)
                except Exception, err:
                    error('error running rclone ls on %s: %s' % (opt.clonedir, err))
                    os.remove(lsoutpath)           # let another worker try
                    return 1
                else:

# make sure DESTID is in the directory listing; if not, something's
# goofy and we don't want to mark all files as missing

                    if lsout.find('33 DESTID') < 0:    # this is a failure
                        error('dir ls not as expected, DESTID not found:\n' + lsout)
                        os.remove(lsoutpath)           # let another worker try
                        return 1
                    n = os.write(lsfd, lsout)
                    if n != len(lsout):
                        error('error writing ls output to %s, tried %d, wrote %d' % (lsoutpath, len(lsout), n))
                    os.rename(lsoutpath, lsoutpath)
            finally:
                if lsfd:
                    os.close(lsfd)
                    lsfd = None

            if not lsout:
                time.sleep(.5)

# search the directory list for the file

        debug('checking dir ls output for filename %s' % vfyfilename)
        pat = '([0-9]+) +%s *$' % re.escape(vfyfilename)
        match = re.search(pat, lsout, re.MULTILINE)
        if not match:
            debug('file %s not found in dir ls' % vfyfilename)
            return 250   # file not there
        debug('dir ls match for %s size %s is "%s", remote size %s' % (vfyfilename, vfysize, match.group(0), match.group(1)))
        if match.group(1) != vfysize:
            debug('file %s remote size is %s, expected %s' % (vfyfilename, match.group(1), vfysize))
            return 249   # size is definitely wrong
        return 0

if __name__ == '__main__':
    rc = main(sys.argv[1:])
    debug('rclone.py returning exit code %d for %s %s' % (rc, opt.command, opt.arg))
    sys.exit(rc)
