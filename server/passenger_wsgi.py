"""
Alternative Passenger entry if Application root = ``server/``.

Preferred layout: Application root = project root (parent of server/)
and use the root-level ``../passenger_wsgi.py``.

Startup file: passenger_wsgi.py  (relative name only).
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

SERVER = Path(__file__).resolve().parent
ROOT = SERVER.parent


def _bootstrap_paths() -> None:
    server_str = str(SERVER)
    if server_str in sys.path:
        sys.path.remove(server_str)
    sys.path.insert(0, server_str)
    try:
        os.chdir(server_str)
    except OSError:
        pass
    for venv_root in (SERVER / ".venv", ROOT / ".venv"):
        if not venv_root.is_dir():
            continue
        lib = venv_root / "lib"
        if not lib.is_dir():
            continue
        for py in lib.iterdir():
            if py.is_dir() and py.name.startswith("python"):
                site = py / "site-packages"
                if site.is_dir() and str(site) not in sys.path:
                    sys.path.insert(0, str(site))
    config_py = SERVER / "app" / "config.py"
    if not config_py.is_file():
        raise RuntimeError(f"Missing {config_py} — upload full server/app/ package.")


def _load_wsgi_application():
    _bootstrap_paths()
    try:
        from app.config import load_env

        load_env()
    except Exception:
        pass
    from a2wsgi import ASGIMiddleware
    from app.factory import create_app

    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    return ASGIMiddleware(create_app())


try:
    application = _load_wsgi_application()
except Exception:  # noqa: BLE001
    _TB = traceback.format_exc()

    def application(environ, start_response):  # type: ignore[no-redef]
        status = "500 Internal Server Error"
        body = (
            "NeurON server/passenger_wsgi.py failed to start.\n\n"
            f"SERVER={SERVER}\nROOT={ROOT}\n\n{_TB}"
        ).encode("utf-8", errors="replace")
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ]
        start_response(status, headers)
        return [body]
