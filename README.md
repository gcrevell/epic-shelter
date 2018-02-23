# Epic Shelter

This is my ongoing project to have a continuous, versioned backup system of my
Plex content, preferably to multiple cloud services. Currently it is rather
basic, serving as little more than a wrapper to [rclone][rc], backing up only to
Google Drive. This is a limitation not only due to the age of this project, but
also because of my 20 mb/s internet upload speed.

Note: the name of this project comes from the Snowden movie.

# Purpose

The purpose of this project is simple. To provide a simple, secure backup of
data to multiple cloud sites.

Because the goal of this project is to eventually be more distributed with
multiple cloud backends, [rclone][rc] was a natural choice. It is a simple
interface for a ton of cloud backends. It also allows a significant amount of
control over what you what.

# Environment

The runtime environment for this script is pretty unique. It is designed to be
run on my QNAP TS-1685 NAS. Due to the way QNAP's OS works, its hard to add new
programs to the `$PATH` variable. Instead, everything has hard coded paths.

It is also designed to be run in a rather slow internet environment, with only
20 mb/s upload speed.

# Contributing

If you have any questions/comments/concerns/suggestions please feel free to make
them. Open an issue, or contact me directly. PRs are also welcome.

# Why?

So, when I was creating these scripts I wasn't planning on putting them in
revision control and sharing them. The scripts weren't that complex and wouldn't
be hard to recreate. However, while I was working on planning this project out,
I came upon a number of "edge cases" with rclone where I had no idea how it
would respond. Through experimentation I was eventually able to track a number
of them down. However, I think it would be good to keep a public record of what
I had tested for so that maybe someone else can learn from it.


[rc]:rclone.org
