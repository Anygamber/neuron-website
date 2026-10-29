"""
cPanel / Phusion Passenger WSGI entrypoint for NeurON FastAPI.

Application root in cPanel must be THIS directory (project root), where
this file lives next to ``server/`` and ``index.html``.

Startup file in cPanel: passenger_wsgi.py
(do NOT paste a full absolute path — that causes «No such WSGI script»).

Passenger speaks WSGI; FastAPI is ASGI → wrapped with a2wsgi.
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "server"


def _bootstrap_paths() -> None:
    # ``import app`` must resolve to server/app (package), not any other ``app``.
    server_str = str(SERVER)
    # Always put server/ first so app.config / app.factory resolve correctly.
    if server_str in sys.path:
        sys.path.remove(server_str)
    sys.path.insert(0, server_str)

    # Working directory: server/ (so .env / data / logs resolve correctly)
    try:
        os.chdir(server_str)
    except OSError:
        pass

    # If Setup Python App venv is not wired, try local venv site-packages
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

    # Fail early with a clear message if package layout is wrong on the host
    config_py = SERVER / "app" / "config.py"
    if not config_py.is_file():
        raise RuntimeError(
            f"Missing {config_py}. Upload the full server/app/ package "
            "(config.py, database.py, factory.py, …)."
        )


def _load_wsgi_application():
    _bootstrap_paths()

    # Load server/.env before importing the app
    try:
        from app.config import load_env

        load_env()
    except Exception:
        pass

    from a2wsgi import ASGIMiddleware
    # Package import (requires server/ on sys.path). Relative imports inside
    # app.factory then resolve .config / .database correctly.
    from app.factory import create_app

    # Optional: quieter under Passenger
    os.environ.setdefault("PYTHONUNBUFFERED", "1")

    return ASGIMiddleware(create_app())


try:
    application = _load_wsgi_application()
except Exception:  # noqa: BLE001 — show import errors in the browser under Passenger
    _TB = traceback.format_exc()

    def application(environ, start_response):  # type: ignore[no-redef]
        status = "500 Internal Server Error"
        body = (
            "NeurON Passenger WSGI failed to start.\n\n"
            "Check: Application root = folder with passenger_wsgi.py;\n"
            "Startup file = passenger_wsgi.py (relative name only);\n"
            "Python App has fastapi + a2wsgi installed.\n\n"
            f"ROOT={ROOT}\nSERVER={SERVER}\nsys.path[0:5]={sys.path[:5]}\n\n"
            f"{_TB}"
        ).encode("utf-8", errors="replace")
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ]
        start_response(status, headers)
        return [body]
