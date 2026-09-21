"""Shared configuration loading for the sync pipeline."""
from __future__ import annotations

from pathlib import Path
import os

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_pixabay_key() -> str | None:
    """Read PIXABAY_KEY from research-blog/.env (no dependency on python-dotenv)."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("PIXABAY_KEY") and "=" in line:
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    return os.environ.get("PIXABAY_KEY") or None


def project_root() -> Path:
    return PROJECT_ROOT
