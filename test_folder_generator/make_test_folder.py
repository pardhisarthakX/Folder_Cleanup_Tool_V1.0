"""
make_test_folder.py
Creates a dummy "messy folder" with sample junk files so you can
safely test the Folder Cleanup Tool without touching real personal files.

Includes: duplicate files, old files, mixed file types, and a few
files with unusual names.

Run with: python make_test_folder.py
"""

import os
import time
from datetime import datetime, timedelta

TEST_FOLDER = "messy_test_folder"


def make_test_folder():
    if not os.path.exists(TEST_FOLDER):
        os.makedirs(TEST_FOLDER)

    # Regular mixed-type files
    write_file("notes.txt", "These are some notes.")
    write_file("photo1.jpg", "fake image data 1")
    write_file("photo2.png", "fake image data 2")
    write_file("budget.xlsx", "fake spreadsheet data")
    write_file("presentation.pptx", "fake slides data")
    write_file("song.mp3", "fake audio data")
    write_file("script.py", "print('hello world')")

    # Duplicate files (identical content, different names)
    write_file("report_final.docx", "This is the final report content.")
    write_file("report_final_copy.docx", "This is the final report content.")
    write_file("report_final_v2.docx", "This is the final report content.")

    # Another duplicate pair
    write_file("vacation.jpg", "beach photo bytes")
    write_file("vacation_copy.jpg", "beach photo bytes")

    # Weird / unicode filenames
    write_file("résumé_final (1).pdf", "fake resume content")
    write_file("file with spaces.txt", "spaced out file")
    write_file("日本語ファイル.txt", "japanese filename test")
    write_file("no_extension_file", "a file with no extension")

    # Old file (simulate by changing modified time to ~1 year ago)
    old_file_path = write_file("old_backup.zip", "old zip content")
    old_time = time.time() - (400 * 24 * 60 * 60)  # ~400 days ago
    os.utime(old_file_path, (old_time, old_time))

    old_file_path2 = write_file("old_notes.txt", "old notes from a while back")
    old_time2 = time.time() - (250 * 24 * 60 * 60)  # ~250 days ago
    os.utime(old_file_path2, (old_time2, old_time2))

    print(f"Test folder created at: ./{TEST_FOLDER}")
    print("Contains: duplicates, old files, mixed types, and unusual filenames.")


def write_file(name, content):
    path = os.path.join(TEST_FOLDER, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


if __name__ == "__main__":
    make_test_folder()
