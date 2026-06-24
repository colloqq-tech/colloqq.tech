from __future__ import annotations

import sys
from pathlib import Path

MODULES_DIR = Path(__file__).resolve().parents[1] / "app" / "modules"
TESTS_DIR = Path(__file__).resolve().parent

for path in (MODULES_DIR, TESTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
