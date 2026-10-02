"""
main.py
Runs the full Folder Cleanup Tool pipeline in this order:
  1. Scan     - collect metadata about every file
  2. Dedupe   - find and move duplicate files to a review folder
  3. Rename   - apply the naming convention
  4. Organize - move files into category subfolders
  5. Archive  - move old files into dated archive folders

Order matters: we dedupe BEFORE renaming/organizing so duplicate
detection compares original file content, not files that have
already been shuffled into subfolders. We rename before organizing
so the final file names are the ones that land in category folders.

This file can be run directly from the command line, or the
run_pipeline() function can be called from ui.py for the Streamlit app.
"""

import os
from typing import Any, Callable, Optional

from folder_cleanup import archiver, deduplicator, organizer, renamer, scanner, undo
from folder_cleanup.config import load_config
from folder_cleanup.logger import get_logger, setup_logging

logger = get_logger(__name__)


def run_pipeline(
    folder_path: str,
    config: dict[str, Any],
    dry_run: Optional[bool] = None,
    recursive: bool = False,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> dict[str, Any]:
    """
    Run the full cleanup pipeline on folder_path using settings from config.
    Returns a summary dictionary with counts for the report.

    Args:
        folder_path: The folder to clean up.
        config: Config dict (from load_config()).
        dry_run: If provided, overrides the dry_run value in config.
        recursive: Whether to scan subfolders.
        progress_callback: Optional callback(step_index, message) invoked
            at each pipeline stage for UI progress reporting.

    Returns:
        Summary dict with counts.
    """
    if dry_run is None:
        dry_run = config.get("dry_run", True)

    undo_log: list[dict] = []  # collects every real action for undo.py

    logger.info("=" * 50)
    logger.info("Starting cleanup on: %s", folder_path)
    logger.info("Dry run: %s", dry_run)
    logger.info("=" * 50)

    # 1. SCAN
    logger.info("--- Step 1: Scanning folder ---")
    if progress_callback:
        progress_callback(0, "Scanning folder...")
    file_list = scanner.scan_folder(folder_path, recursive=recursive)
    logger.info("Found %d files.", len(file_list))

    total_size_before = sum(f["size_bytes"] for f in file_list)

    # 2. DEDUPLICATE
    logger.info("--- Step 2: Checking for duplicates ---")
    if progress_callback:
        progress_callback(1, "Checking for duplicates...")
    duplicate_groups = deduplicator.find_duplicates(file_list)
    review_folder = os.path.join(folder_path, "review_duplicates")
    duplicates_moved = deduplicator.move_duplicates_to_review(
        duplicate_groups, review_folder, dry_run=dry_run, undo_log=undo_log
    )

    # Refresh file list so we don't process files that were just moved out
    file_list = [f for f in file_list if os.path.exists(f["path"])]

    # 3. RENAME
    logger.info("--- Step 3: Renaming files ---")
    if progress_callback:
        progress_callback(2, "Renaming files...")
    pattern = config.get("rename_pattern", "{name}{ext}")
    renamed = renamer.rename_files(file_list, pattern, dry_run=dry_run, undo_log=undo_log)

    # 4. ORGANIZE
    logger.info("--- Step 4: Organizing files into categories ---")
    if progress_callback:
        progress_callback(3, "Organizing files into categories...")
    categories = config.get("categories", {})
    organized = organizer.organize_files(
        file_list, categories, folder_path, dry_run=dry_run, undo_log=undo_log
    )

    # 5. ARCHIVE
    logger.info("--- Step 5: Archiving old files ---")
    if progress_callback:
        progress_callback(4, "Archiving old files...")
    age_days = config.get("archive_age_days", 180)
    archived = archiver.archive_old_files(
        file_list, folder_path, age_days, dry_run=dry_run, undo_log=undo_log
    )

    # Save undo log if this was a real run
    if not dry_run and undo_log:
        undo.save_undo_log(undo_log)
        logger.info("Undo log saved with %d actions. Run undo.py to reverse.", len(undo_log))

    summary = {
        "files_scanned": len(file_list),
        "duplicates_found": duplicates_moved,
        "files_renamed": renamed,
        "files_organized": organized,
        "files_archived": archived,
        "total_size_before_bytes": total_size_before,
        "dry_run": dry_run,
    }

    logger.info("=" * 50)
    logger.info("SUMMARY")
    logger.info("=" * 50)
    for key, value in summary.items():
        logger.info("%s: %s", key, value)

    return summary


def main() -> None:
    """CLI entry point for the Folder Cleanup Tool."""
    setup_logging()

    folder = input("Enter the folder path to clean up: ").strip()

    if not os.path.isdir(folder):
        print("That folder path does not exist. Exiting.")
    else:
        cfg = load_config()

        dry_run_input = input("Run in dry-run mode first? (y/n): ").strip().lower()
        dry_run_flag = True if dry_run_input == "y" else False

        run_pipeline(folder, cfg, dry_run=dry_run_flag)


if __name__ == "__main__":
    main()
