"""Load the solution-tradeoff settings file.

The shipped defaults live in ``assets/config.yaml``. Every script accepts
``--config <path>`` to use another file with the same structure.
"""

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "assets" / "config.yaml"


def load_settings(path: Path | None = None) -> dict[str, Any]:
    """Read a settings file.

    Args:
        path: Settings file to read. Defaults to the shipped ``assets/config.yaml``.

    Returns:
        The parsed settings mapping.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not valid YAML or not a mapping.
    """
    path = path or DEFAULT_CONFIG
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Settings file '{path}' is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Settings file '{path}' must contain a mapping.")
    return data
