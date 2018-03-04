# Backing up Radarr database
#QNAP/EpicShelter

The Radarr database contains the information about what movies I have added to it. For the most part, these are movies that I have in my library, though not all are. Some are new movies that I don’t have a copy of yet because they are yet to be released.

The database also contains all of my settings. They dictate what quality each show should be grabbed at, and what the quality profiles mean.

### Why
This is part of project: Epic Shelter. Its a periodic backup of the database so I can restore it and at the bare minimum have a list of the movies I had before.

### How
Backing up is surprisingly easy, because of the script I wrote. It’s in the GitHub epic-shelter repo under the `RADARR` directory. It will use the Radarr API to start a new backup of the database, then download the backup, encrypt it using `openssl`, and copy it up to Google Drive.

For encryption, I am using `openssl`’s `aes-256-cbc` encryption mode, and the password is in 1password. 

The script is designed to run from my personal Mac instead of my QNAP because it is easier to pass secrets into the scripts that way.

To run the script, three environment variables are required. They are:

* `RADARR_API_KEY` - The API key for Radarr authentication.
* `RADARR_BACKUP_PASSWORD` - The password `openssl` uses to encrypt the zip file.
* `RADARR_URL` - The URL for Radarr. I don’t want to share this publicly.

### Automation
This script is automated, using a Mac `launchd` command. It should run once a day, at midnight. It uses a `launchd` timed command instead of `cron`, because if the computer is asleep during the scheduled run time, it will run on wake instead of not running at all.