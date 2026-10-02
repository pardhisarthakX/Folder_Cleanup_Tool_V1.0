"""
renamer.py
Renames files according to a pattern defined in config.json.
Every rename is logged so it can be undone later.
"""

import os
from typing import Optional

from folder_cleanup.logger import get_logger
from folder_cleanup.utils import get_unique_path

logger = get_logger(__name__)


def rename_files(
    file_list: list[dict],
    pattern: str,
    dry_run: bool = True,
    undo_log: Optional[list[dict]] = None,
) -> int:
    """
    Rename each file in file_list according to 'pattern'.

    Args:
        file_list: List of file info dicts (from scanner.py).
        pattern: Naming pattern string, e.g. "{name}_{date}{ext}".
            Supported placeholders:
              {name} - original file name (without extension)
              {ext}  - file extension, including the dot
              {date} - modified date as YYYY-MM-DD
        dry_run: If True, only print what would happen.
        undo_log: List to record actions for undo.py (optional).

    Returns:
        Number of files renamed.
    """
    renamed_count = 0

    for file_info in file_list:
        old_path = file_info["path"]

        # Skip if the file no longer exists (may have been moved already)
        if not os.path.exists(old_path):
            continue

        new_name = build_new_name(file_info, pattern)
        folder = os.path.dirname(old_path)
        new_path = os.path.join(folder, new_name)

        # Don't rename if the new name is the same as the old one
        if new_path == old_path:
            continue

        new_path = get_unique_path(new_path)

        if dry_run:
            logger.info("[DRY RUN] Would rename: %s -> %s", old_path, new_path)
        else:
            os.rename(old_path, new_path)
            logger.info("Renamed: %s -> %s", old_path, new_path)
            if undo_log is not None:
                undo_log.append(
                    {
                        "action": "rename",
                        "old_path": old_path,
                        "new_path": new_path,
                    }
                )
            # Update the file_info so later steps (organize/archive)
            # know about the new path and name
            file_info["path"] = new_path
            file_info["name"] = os.path.basename(new_path)

        renamed_count += 1

    logger.info("Total files renamed: %d", renamed_count)
    return renamed_count


def build_new_name(file_info: dict, pattern: str) -> str:
    """
    Build a new file name from the pattern and the file's metadata.

    Args:
        file_info: File info dict.
        pattern: Naming pattern string.

    Returns:
        The new file name.
    """
    date_str = file_info["modified_date"].strftime("%Y-%m-%d")

    new_name = pattern.format(
        name=file_info["name_only"],
        ext=file_info["extension"],
        date=date_str,
    )
    return new_name
