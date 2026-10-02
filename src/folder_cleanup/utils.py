"""
utils.py
Shared utility functions used across the Folder Cleanup Tool.
Centralizes the 'get_unique_path' logic that was previously
duplicated in multiple modules.
"""

import os


def get_unique_path(path: str) -> str:
    """
    If a file already exists at 'path', add a number to the filename
    until the path is free. Prevents accidentally overwriting files.

    Args:
        path: The desired file path.

    Returns:
        A path that does not currently exist on disk.
    """
    if not os.path.exists(path):
        return path

    folder = os.path.dirname(path)
    file_name = os.path.basename(path)
    name_only, extension = os.path.splitext(file_name)

    counter = 1
    while True:
        new_name = f"{name_only}_{counter}{extension}"
        new_path = os.path.join(folder, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def safe_move(src: str, dst: str) -> None:
    """
    Atomically move a file using a temporary path + rename to reduce
    the risk of corruption on interruption.

    Args:
        src: Source file path.
        dst: Destination file path.
    """
    import shutil

    # If dst doesn't exist, a plain move is fine
    if not os.path.exists(dst):
        shutil.move(src, dst)
        return

    # Otherwise, move to a temp name then rename into place
    temp_path = dst + ".tmp"
    shutil.move(src, temp_path)
    os.replace(temp_path, dst)
