import os

def create_folder(path_to_folder: str):
    """Create folder if it does not exist already.

    Args:
        path_to_folder: Path to folder to create.
    """
    if not os.path.exists(path_to_folder):
        print(f"Directory does not exist! Making directory {path_to_folder}.")
        os.mkdir(path_to_folder)
    else:
        print(f"Directory {path_to_folder} already exists! ")
