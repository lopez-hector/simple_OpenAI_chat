import os
import glob
from pathlib import Path


def get_most_recent_file(directory):
    os.chdir(directory)
    files = sorted(glob.glob("*/*"), key=os.path.getctime, reverse=True)
    if files:
        return files[0]
    else:
        return None


directory_path = '/Users/hectorlopezhernandez/PycharmProjects/chat/img'

most_recent_file = Path(get_most_recent_file(directory_path))

print(most_recent_file)
