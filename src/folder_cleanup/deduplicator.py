"""
deduplicator.py
Finds duplicate files by comparing their content hashes (not just names).
Duplicates are never deleted automatically - they are moved into a
"review" folder so the user can check them before removing anything.
"""

import hashlib
import os
import shutil
from typing import Optional

from folder_cleanup.logger import get_logger
from folder_cleanup.utils import get_unique_path

logger = get_logger(__name__)


def hash_file(file_path: str, chunk_size: int = 8192) -> Optional[str]:
    """
    Compute the SHA-256 hash of a file's contents.
    Reads the file in small chunks so large files don't
    get loaded into memory all at once.

    Args:
        file_path: Path to the file to hash.
        chunk_size: Size (in bytes) of each read chunk.

    Returns:
        The SHA-256 hex digest, or None if the file can't be read.
    """
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError, OSError):
        logger.warning("Could not hash file: %s", file_path)
        return None


def find_duplicates(file_list: list[dict]) -> dict[str, list[str]]:
    """
    Given a list of file info dicts (from scanner.py), group files
    by their content hash. Returns a dictionary where each key is
    a hash and each value is a list of file paths that share that hash.
    Only hashes with more than 1 file are actual duplicate groups.

    Args:
        file_list: List of file info dicts.

    Returns:
        Dict mapping hash -> list of file paths (duplicate groups only).
    """
    hash_groups: dict[str, list[str]] = {}

    for file_info in file_list:
        file_hash = hash_file(file_info["path"])
        if file_hash is None:
            continue

        if file_hash not in hash_groups:
            hash_groups[file_hash] = []
        hash_groups[file_hash].append(file_info["path"])

    # Keep only groups that actually have duplicates
    duplicate_groups = {
        file_hash: paths for file_hash, paths in hash_groups.items() if len(paths) > 1
    }

    logger.info("Found %d duplicate groups", len(duplicate_groups))
    return duplicate_groups


def move_duplicates_to_review(
    duplicate_groups: dict[str, list[str]],
    review_folder: str,
    dry_run: bool = True,
    undo_log: Optional[list[dict]] = None,
) -> int:
    """
    For each group of duplicates, keep the FIRST file where it is
    and move the rest into the review folder.

    Args:
        duplicate_groups: Output of find_duplicates().
        review_folder: Folder to move extra copies into.
        dry_run: If True, only print what would happen.
        undo_log: List to record actions for undo.py (optional).

    Returns:
        Number of files moved.
    """
    if not dry_run and not os.path.exists(review_folder):
        os.makedirs(review_folder)

    moved_count = 0

    for file_hash, paths in duplicate_groups.items():
        # Keep the first file, move the rest
        keep_file = paths[0]
        extra_files = paths[1:]

        logger.info("Duplicate group (keeping: %s):", keep_file)

        for extra_path in extra_files:
            file_name = os.path.basename(extra_path)
            new_path = os.path.join(review_folder, file_name)

            # Avoid overwriting a file that's already in review_folder
            new_path = get_unique_path(new_path)

            if dry_run:
                logger.info("[DRY RUN] Would move: %s -> %s", extra_path, new_path)
            else:
                shutil.move(extra_path, new_path)
                logger.info("Moved: %s -> %s", extra_path, new_path)
                if undo_log is not None:
                    undo_log.append(
                        {
                            "action": "move",
                            "old_path": extra_path,
                            "new_path": new_path,
                        }
                    )
            moved_count += 1

    logger.info("Total duplicate files handled: %d", moved_count)
    return moved_count
