import os
import json
from gitshorts.utils.colors import Printer


CONFIG_DIR  = os.path.expanduser("~/.gitshorts")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


# default config
DEFAULTS = {
    "merge": {
        "strategy":        "smart",    # smart/ours/theirs/longer
        "auto_backup":     True,       # backup before resolving
        "backup_retention": 7,         # days to keep backups
        "dry_run":         False,      # always dry run first
    },
    "push": {
        "auto_fix":        True,       # auto fix push errors
        "auto_pull":       True,       # auto pull if remote ahead
        "large_file_warn": 100,        # MB threshold for warning
        "max_retries":     2,          # max push retry attempts
    },
    "token": {
        "expiry_warn_days": 14,        # warn N days before expiry
        "auto_refresh":    False,      # auto refresh expired tokens
    },
    "output": {
        "colors":          True,       # enable colors
        "verbose":         False,      # verbose output
        "emoji":           False,      # use emoji in output
    },
    "shortcuts": {
        "confirm_gnuke":   True,       # confirm before gnuke
        "auto_stage":      True,       # auto stage in gcp
    }
}


def load():
    """Load config — falls back to defaults for missing keys"""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULTS.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            user_config = json.load(f)

        # merge with defaults — user overrides defaults
        config = DEFAULTS.copy()
        for section, values in user_config.items():
            if section in config:
                config[section].update(values)

        return config

    except Exception:
        Printer.warning("Config file corrupted — using defaults")
        return DEFAULTS.copy()


def save(config):
    """Save config to file"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        Printer.success(f"Config saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        Printer.error(f"Failed to save config: {e}")
        return False


def get(section, key, fallback=None):
    """Get a single config value"""
    config = load()
    return config.get(section, {}).get(key, fallback)


def set_value(section, key, value):
    """Set a single config value"""
    config = load()
    if section not in config:
        config[section] = {}
    config[section][key] = value
    return save(config)


def reset():
    """Reset config to defaults"""
    return save(DEFAULTS.copy())


def display():
    """Show current config"""
    config = load()
    Printer.header("gitshorts config")

    for section, values in config.items():
        print(f"\n  [{section}]")
        for key, value in values.items():
            print(f"  {key:<20} = {value}")

    print("")
    print(f"  Config file: {CONFIG_FILE}")
    Printer.divider()


def gconfig(action=None, section=None, key=None, value=None):
    """
    Main config command
    gconfig                     → show all config
    gconfig reset               → reset to defaults
    gconfig set merge strategy ours   → set value
    gconfig get merge strategy        → get value
    """
    if not action or action == "show":
        display()

    elif action == "reset":
        confirm = input("  Reset all config to defaults? (y/N): ").strip().lower()
        if confirm == "y":
            reset()
            Printer.success("Config reset to defaults")
        else:
            Printer.info("Cancelled")

    elif action == "set":
        if not section or not key or value is None:
            Printer.error("Usage: gconfig set <section> <key> <value>")
            return
        # convert string values
        if value.lower() == "true":  value = True
        elif value.lower() == "false": value = False
        elif value.isdigit():         value = int(value)

        set_value(section, key, value)
        Printer.success(f"Set {section}.{key} = {value}")

    elif action == "get":
        if not section or not key:
            Printer.error("Usage: gconfig get <section> <key>")
            return
        value = get(section, key)
        print(f"  {section}.{key} = {value}")

    else:
        Printer.error(f"Unknown action: {action}")
        print("  Usage: gconfig [show|set|get|reset]")
