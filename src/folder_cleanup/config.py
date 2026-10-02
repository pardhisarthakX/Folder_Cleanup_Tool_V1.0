"""
config.py
Configuration loading and validation for the Folder Cleanup Tool.

Supports a 12-factor approach: config.json provides defaults, and
environment variables can override any setting. Also validates the
configuration schema and gives friendly error messages on bad input.
"""

import json
import os
from typing import Any

from dotenv import load_dotenv

# Default config path relative to project root
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json"
)

# Expected config structure (for validation)
REQUIRED_KEYS = {"dry_run", "archive_age_days", "rename_pattern", "categories"}
CATEGORY_KEYS = {
    "Images",
    "Documents",
    "Spreadsheets",
    "Presentations",
    "Audio",
    "Video",
    "Archives",
    "Code",
    "Other",
}

# Env-var mapping: config key -> (env var name, type)
ENV_MAPPINGS = {
    "dry_run": ("FOLDER_CLEANUP_DRY_RUN", "bool"),
    "archive_age_days": ("FOLDER_CLEANUP_ARCHIVE_AGE_DAYS", "int"),
    "rename_pattern": ("FOLDER_CLEANUP_RENAME_PATTERN", "str"),
}


def load_config(config_path: str = DEFAULT_CONFIG_PATH, use_env: bool = True) -> dict[str, Any]:
    """
    Load configuration from a JSON file, optionally overridden by env vars.

    Args:
        config_path: Path to the JSON config file.
        use_env: Whether to apply environment variable overrides.

    Returns:
        A validated config dictionary.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If the config is invalid.
    """
    # Load .env file if present (for local dev)
    if use_env:
        load_dotenv()

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a JSON object at the top level.")

    validate_config(config)

    if use_env:
        apply_env_overrides(config)

    return config


def validate_config(config: dict[str, Any]) -> None:
    """
    Validate the config structure and raise friendly errors on problems.

    Args:
        config: The loaded config dictionary.

    Raises:
        ValueError: If the config is missing required keys or has invalid values.
    """
    missing = REQUIRED_KEYS - set(config.keys())
    if missing:
        raise ValueError(f"Config is missing required keys: {sorted(missing)}")

    # dry_run must be a bool
    if not isinstance(config.get("dry_run"), bool):
        raise ValueError("Config 'dry_run' must be a boolean (true/false).")

    # archive_age_days must be a positive int
    age = config.get("archive_age_days")
    if not isinstance(age, int) or age < 0:
        raise ValueError("Config 'archive_age_days' must be a non-negative integer.")

    # rename_pattern must be a string
    if not isinstance(config.get("rename_pattern"), str):
        raise ValueError("Config 'rename_pattern' must be a string.")

    # categories must be a dict of str -> list of str
    categories = config.get("categories")
    if not isinstance(categories, dict):
        raise ValueError("Config 'categories' must be an object.")

    for category, extensions in categories.items():
        if not isinstance(extensions, list) or not all(isinstance(e, str) for e in extensions):
            raise ValueError(f"Config category '{category}' must be a list of extension strings.")
        # Normalize extensions to start with a dot
        categories[category] = [e if e.startswith(".") else f".{e}" for e in extensions]


def apply_env_overrides(config: dict[str, Any]) -> None:
    """
    Apply environment variable overrides to the config dict (in-place).

    Args:
        config: The config dict to modify.
    """
    for key, (env_var, env_type) in ENV_MAPPINGS.items():
        value = os.getenv(env_var)
        if value is None:
            continue

        try:
            if env_type == "bool":
                config[key] = value.strip().lower() in ("1", "true", "yes", "y")
            elif env_type == "int":
                config[key] = int(value)
            elif env_type == "str":
                config[key] = value
        except ValueError:
            # Leave the config default if env var is malformed
            print(f"Warning: Invalid value for env var {env_var}: {value!r}. Using default.")


if __name__ == "__main__":
    cfg = load_config()
    print("Config loaded successfully:")
    print(json.dumps(cfg, indent=2, default=str))
