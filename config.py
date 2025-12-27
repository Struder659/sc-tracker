import os

TARGET_PROFILE_URL = "https://soundcloud.com/youruser/tracks"
CHECK_INTERVAL = 100
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "output")
ARCHIVE_FILE = os.path.join(os.getcwd(), "archive.txt")
LOG_FILE = os.path.join(os.getcwd(), "tracker_debug.log")