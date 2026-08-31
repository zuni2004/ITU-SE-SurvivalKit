import os
import hashlib
import json
from datetime import datetime

STATE_FILE = "file_hashes.json"
LOG_FILE = "integrity_monitor.log"


def get_file_hash(filepath):
    """Calculates the SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return None


def scan_directory(folder_path):
    """Scans the directory and returns a dictionary of file paths and their hashes."""
    file_hashes = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            filepath = os.path.join(root, file)
            file_hash = get_file_hash(filepath)
            if file_hash:
                file_hashes[filepath] = file_hash
    return file_hashes


def log_change(message):
    """Logs changes with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")


def run_integrity_check(folder_path):
    print(f"Scanning folder: {folder_path}...")
    current_hashes = scan_directory(folder_path)

    # If no state file exists, this is the first run.
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump(current_hashes, f)
        log_change("Initial scan complete. Baseline hashes saved.")
        return

    # Load stored hashes
    with open(STATE_FILE, "r") as f:
        stored_hashes = json.load(f)

    changes_detected = False

    # Check for Modified and Added files
    for filepath, current_hash in current_hashes.items():
        if filepath not in stored_hashes:
            log_change(f"ADDED: {filepath}")
            changes_detected = True
        elif stored_hashes[filepath] != current_hash:
            log_change(f"MODIFIED: {filepath}")
            changes_detected = True

    # Check for Deleted files
    for filepath in stored_hashes.keys():
        if filepath not in current_hashes:
            log_change(f"DELETED: {filepath}")
            changes_detected = True

    if not changes_detected:
        log_change("Scan complete. No changes detected.")

    # Update state file with current hashes
    with open(STATE_FILE, "w") as f:
        json.dump(current_hashes, f)


if __name__ == "__main__":
    # Target folder (Create this folder and put 20+ files in it before running)
    TARGET_DIR = "./test_folder"

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(
            f"Created '{TARGET_DIR}'. Please populate it with at least 20 files and run this script again."
        )
    else:
        run_integrity_check(TARGET_DIR)
