import os
import shutil
from datetime import datetime
from gitshorts.utils.colors import Printer


def create_backup(filepath):
    """Backup a file before resolving conflicts"""
    if not os.path.exists(filepath):
        Printer.error(f"File not found: {filepath}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.gitfast_backup_{timestamp}"

    try:
        shutil.copy2(filepath, backup_path)
        Printer.step(f"Backed up: {backup_path}")
        return backup_path
    except Exception as e:
        Printer.error(f"Backup failed: {e}")
        return None


def restore_backup(backup_path):
    """Restore a file from backup"""
    if not os.path.exists(backup_path):
        Printer.error(f"Backup not found: {backup_path}")
        return False

    # get original path
    original = _get_original_path(backup_path)
    if not original:
        Printer.error("Could not determine original path")
        return False

    try:
        shutil.copy2(backup_path, original)
        Printer.success(f"Restored: {original}")
        return True
    except Exception as e:
        Printer.error(f"Restore failed: {e}")
        return False


def delete_backup(backup_path):
    """Delete a backup file after successful resolve"""
    if not os.path.exists(backup_path):
        return True

    try:
        os.remove(backup_path)
        Printer.step(f"Backup removed: {backup_path}")
        return True
    except Exception as e:
        Printer.error(f"Failed to delete backup: {e}")
        return False


def list_backups(directory="."):
    """List all gitfast backup files"""
    backups = []

    for root, dirs, files in os.walk(directory):
        for f in files:
            if ".gitfast_backup_" in f:
                backups.append(os.path.join(root, f))

    if not backups:
        Printer.info("No backups found")
    else:
        Printer.header("gitfast Backups")
        for b in backups:
            print(f"  {b}")
        Printer.divider()

    return backups


def cleanup_backups(directory="."):
    """Delete all backup files"""
    backups = list_backups(directory)

    if not backups:
        return True

    confirm = input(f"Delete {len(backups)} backup files? (y/N): ").strip().lower()
    if confirm != "y":
        Printer.info("Cancelled")
        return False

    for b in backups:
        delete_backup(b)

    Printer.success(f"Cleaned up {len(backups)} backups")
    return True


def _get_original_path(backup_path):
    """Extract original filepath from backup path"""
    marker = ".gitfast_backup_"
    idx = backup_path.find(marker)
    if idx == -1:
        return None
    return backup_path[:idx]
