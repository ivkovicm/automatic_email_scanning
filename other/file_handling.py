import os
import shutil


def rm_file(file_for_cleaning: str) -> None:
    try:
        os.remove(file_for_cleaning)
    except OSError:
        logging.error("File {} not found for erasing!".format(file_for_cleaning))
    except IsADirectoryError:
        logging.error("File {} isn't file but a directory!".format(file_for_cleaning))


def save_file(full_path: str, payload: str) -> None:
    try:
        with open(full_path, "w") as fh:
            fh.write(payload)
    except OSError:
        logging.error("File couldn't be saved to {}!".format(full_path))


def move_file(source: str, destination: str) -> None:
    try:
        shutil.move(source, destination)
    except:
        logging.error("File couldn't be moved from {} to {}!".format(source, destination))
