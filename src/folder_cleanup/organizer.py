"""
organizer.py
Moves files into category subfolders (Images, Documents, etc.)
based on the extension mapping in config.json.
"""

import os
import shutil
from typing import Optional

from folder_cleanup.logger import get_logger
from folder_cleanup.utils import get_unique_path

logger = get_logger(__name__)


def organize_files(
    file_list: list[dict],
    categories: dict[str, list[str]],
    base_folder: str,
    dry_run: bool = True,
    undo_log: Optional[list[dict]] = None,
) -> int:
    """
    Move each file into a subfolder named after its category.

    Args:
        file_list: List of file info dicts (from scanner.py).
        categories: Dict mapping category name -> list of extensions
            (loaded from config.json).
        base_folder: The root folder where category subfolders will be created.
        dry_run: If True, only print what would happen.
        undo_log: List to record actions for undo.py (optional).

    Returns:
        Number of files organized.
    """
    organized_count = 0

    for file_info in file_list:
        old_path = file_info["path"]

        if not os.path.exists(old_path):
            continue

        category = get_category(file_info["extension"], categories)
        category_folder = os.path.join(base_folder, category)

        if not dry_run and not os.path.exists(category_folder):
            os.makedirs(category_folder)

        new_path = os.path.join(category_folder, file_info["name"])
        new_path = get_unique_path(new_path)

        # Skip if it's already in the right place
        if new_path == old_path:
            continue

        if dry_run:
            logger.info("[DRY RUN] Would move: %s -> %s", old_path, new_path)
        else:
            shutil.move(old_path, new_path)
            logger.info("Moved: %s -> %s", old_path, new_path)
            if undo_log is not None:
                undo_log.append(
                    {
                        "action": "move",
                        "old_path": old_path,
                        "new_path": new_path,
                    }
                )
            file_info["path"] = new_path

        organized_count += 1

    logger.info("Total files organized: %d", organized_count)
    return organized_count


def get_category(extension: str, categories: dict[str, list[str]]) -> str:
    """
    Look up which category a file extension belongs to.
    Returns "Other" if no match is found.

    Args:
        extension: File extension (with dot, e.g. ".jpg").
        categories: Category mapping from config.

    Returns:
        The category name, or "Other".
    """
    for category_name, extensions in categories.items():
        if extension in extensions:
            return category_name
    return "Other"
