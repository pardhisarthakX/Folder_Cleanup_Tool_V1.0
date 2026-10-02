"""
undo.py
Reads logs/undo_log.json and reverses every action in it,
starting from the most recent action and working backwards.
This puts files back where they were before the last real run.
"""

import json
import os
import shutil

from folder_cleanup.logger import get_logger

logger = get_logger(__name__)

UNDO_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "undo_log.json"
)


def load_undo_log(log_path: str = UNDO_LOG_PATH) -> list[dict]:
    """
    Load the undo log file. Returns an empty list if it doesn't exist.

    Args:
        log_path: Path to the undo log file.

    Returns:
        List of action dicts.
    """
    if not os.path.exists(log_path):
        logger.info("No undo log found - nothing to undo.")
        return []

    with open(log_path, encoding="utf-8") as f:
        return json.load(f)


def undo_actions(log_path: str = UNDO_LOG_PATH) -> int:
    """
    Reverse every action in the undo log, most recent first.
    A "move" or "rename" action is reversed by moving the file
    from new_path back to old_path.

    Args:
        log_path: Path to the undo log file.

    Returns:
        Number of actions undone.
    """
    actions = load_undo_log(log_path)

    if not actions:
        return 0

    # Reverse in the opposite order they were applied
    reversed_actions = list(reversed(actions))
    undone_count = 0

    for action in reversed_actions:
        old_path = action["old_path"]
        new_path = action["new_path"]

        if not os.path.exists(new_path):
            logger.warning("Skipping (file not found): %s", new_path)
            continue

        # Make sure the original folder still exists
        old_folder = os.path.dirname(old_path)
        if not os.path.exists(old_folder):
            os.makedirs(old_folder)

        shutil.move(new_path, old_path)
        logger.info("Restored: %s -> %s", new_path, old_path)
        undone_count += 1

    logger.info("Total actions undone: %d", undone_count)

    # Clear the log after a successful undo so it can't be run twice
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump([], f)

    return undone_count


def save_undo_log(actions: list[dict], log_path: str = UNDO_LOG_PATH) -> None:
    """
    Save the list of actions recorded during a real run.

    Args:
        actions: List of action dicts.
        log_path: Path to the undo log file.
    """
    log_folder = os.path.dirname(log_path)
    if log_folder and not os.path.exists(log_folder):
        os.makedirs(log_folder)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=2, default=str)


if __name__ == "__main__":
    confirm = input("This will undo the last cleanup run. Continue? (y/n): ")
    if confirm.lower() == "y":
        undo_actions()
    else:
        print("Undo cancelled.")
