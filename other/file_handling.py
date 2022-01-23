import os


def rm_file(file_for_cleaning) -> None:
    try:
        os.remove(file_for_cleaning)
    except OSError:
        logging.error("File {} not found for erasing!".format(file_for_cleaning))
    except IsADirectoryError:
        logging.error("File {} isn't file but a directory!".format(file_for_cleaning))


def save_file(full_path) -> None:
    try:
        with open(full_path, "w") as fh:
            fh.write()
    except OSError:
        logging.error("File couldn't be saved to {}!".format(full_path))
