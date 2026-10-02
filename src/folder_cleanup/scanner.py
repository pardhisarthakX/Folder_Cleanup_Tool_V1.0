"""
scanner.py
Walks a target folder and collects metadata about every file inside it.
Each file's info is stored as a simple dictionary so it's easy to pass
around between the other modules.
"""

import os
from datetime import datetime
from typing import Optional

from folder_cleanup.logger import get_logger

logger = get_logger(__name__)


def scan_folder(folder_path: str, recursive: bool = False) -> list[dict]:
    """
    Walk the given folder and return a list of dictionaries,
    one per file, with metadata about that file.

    Args:
        folder_path: Path to the folder to scan.
        recursive: If True, also scan subfolders. If False, only
            scan the top-level files in folder_path.

    Returns:
        List of file info dicts.
    """
    file_list: list[dict] = []

    if recursive:
        # os.walk goes into every subfolder automatically
        for root, _dirs, files in os.walk(folder_path):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                info = get_file_info(full_path)
                if info is not None:
                    file_list.append(info)
    else:
        # Only look at files directly inside folder_path
        for file_name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file_name)
            if os.path.isfile(full_path):
                info = get_file_info(full_path)
                if info is not None:
                    file_list.append(info)

    logger.info("Scanned %d files in %s (recursive=%s)", len(file_list), folder_path, recursive)
    return file_list


def get_file_info(full_path: str) -> Optional[dict]:
    """
    Return a dictionary of metadata for a single file.
    Returns None if the file can't be read (e.g. permission error).

    Args:
        full_path: Full path to the file.

    Returns:
        Dict of file metadata, or None on error.
    """
    try:
        stats = os.stat(full_path)
        file_name = os.path.basename(full_path)
        name_only, extension = os.path.splitext(file_name)

        info = {
            "name": file_name,
            "name_only": name_only,
            "extension": extension.lower(),
            "path": full_path,
            "size_bytes": stats.st_size,
            "modified_date": datetime.fromtimestamp(stats.st_mtime),
            "created_date": datetime.fromtimestamp(stats.st_ctime),
        }
        return info

    except (PermissionError, FileNotFoundError, OSError):
        logger.warning("Skipping file (could not read): %s", full_path)
        return None


# Quick manual test when running this file directly
if __name__ == "__main__":
    test_path = input("Enter a folder path to scan: ")
    results = scan_folder(test_path)
    print(f"\nFound {len(results)} files:\n")
    for f in results:
        print(f"{f['name']}  |  {f['size_bytes']} bytes  |  modified {f['modified_date']}")
