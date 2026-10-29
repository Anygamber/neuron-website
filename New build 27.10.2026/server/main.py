"""Entry re-export for hosting panels that look for server/main.py.

ASGI app object: ``app`` (FastAPI).
Under cPanel Passenger use ``passenger_wsgi.py`` (WSGI via a2wsgi), not this file.

Imports ``create_app`` from ``app.factory`` (not ``app.main``) to avoid
circular import: server/main → app.main → … → server/main.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure this directory (server/) is on sys.path when panels load main.py directly
_SERVER_DIR = Path(__file__).resolve().parent
if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))

from app.factory import create_app

app = create_app()

__all__ = ["app", "create_app"]
