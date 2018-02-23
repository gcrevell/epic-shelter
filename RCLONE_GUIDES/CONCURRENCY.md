# The issue

What if you had multiple instances of rclone running simultaneously in the same
folder, uploading to the same remote? This issue came up in the context of
using rclone as a backup system. So it would be running on a timer, perhaps as a
`cron` job. What if a second backup had started before the first had finished?
What would happen when trying to upload the files if both instances attempted to
upload the same file at the same time?

# The environment

This test was run on MacOS, using rclone 1.39. The destination remote was an
unencrypted Google Drive.

# The test

For the test, I decided to create a file of random data using `dd`.

```
dd if=/dev/urandom of=Test/sample.txt bs=1024 count=1048576
```

This creates a file of random bits with a total size of 1 [GiB][BS]. This is
what we will use for our test upload file. To upload, I started 2 instances of
rclone with identical parameters in separate terminals.

```
rclone -v --stats 15s sync Test GDrive:Test
```

This makes the whole script

```
mkdir Test
dd if=/dev/urandom of=Test/sample.txt bs=1024 count=1048576
rclone -v --stats 15s sync Test GDrive:Test
```

Then run the rclone command again in another window from the same directory.

# The results

Both scripts ran successfully without errors and uploaded the file. However, I
then ended up with 2 copies of the file on the remote. Maybe if I was uploading
to a remote that couldn't have files with the same name in a directory something
different would have happened.

# TL;DR

Uploading a file from 2 different rclone instances to Google Drive causes 2
copies to appear on the remote.

[BS]:https://www.linkedin.com/pulse/20140814132922-176099595-mb-vs-mib-gb-vs-gib
