"""
archiver.py
Checks each file's modified date against an age threshold (in days).
Files older than the threshold get moved into an "Archive" folder,
grouped by year.
"""

import os
import shutil
from datetime import datetime
from typing import Optional

from folder_cleanup.logger import get_logger
from folder_cleanup.utils import get_unique_path

logger = get_logger(__name__)


def archive_old_files(
    file_list: list[dict],
    base_folder: str,
    age_days: int,
    dry_run: bool = True,
    undo_log: Optional[list[dict]] = None,
) -> int:
    """
    Move files older than 'age_days' into Archive/<year>/ subfolders.

    Args:
        file_list: List of file info dicts (from scanner.py).
        base_folder: Root folder where the Archive folder will be created.
        age_days: Files with modified date older than this many days
            get archived.
        dry_run: If True, only print what would happen.
        undo_log: List to record actions for undo.py (optional).

    Returns:
        Number of files archived.
    """
    archived_count = 0
    today = datetime.now()

    for file_info in file_list:
        old_path = file_info["path"]

        if not os.path.exists(old_path):
            continue

        age_in_days = (today - file_info["modified_date"]).days

        if age_in_days < age_days:
            continue  # file is not old enough to archive

        year = file_info["modified_date"].year
        archive_folder = os.path.join(base_folder, "Archive", str(year))

        if not dry_run and not os.path.exists(archive_folder):
            os.makedirs(archive_folder)

        new_path = os.path.join(archive_folder, file_info["name"])
        new_path = get_unique_path(new_path)

        if new_path == old_path:
            continue

        if dry_run:
            logger.info(
                "[DRY RUN] Would archive: %s -> %s  (%d days old)",
                old_path,
                new_path,
                age_in_days,
            )
        else:
            shutil.move(old_path, new_path)
            logger.info("Archived: %s -> %s", old_path, new_path)
            if undo_log is not None:
                undo_log.append(
                    {
                        "action": "move",
                        "old_path": old_path,
                        "new_path": new_path,
                    }
                )
            file_info["path"] = new_path

        archived_count += 1

    logger.info("Total files archived: %d", archived_count)
    return archived_count
