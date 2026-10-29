"""ASGI entry: ``app.main:app``.

Application object is created in ``app.factory.create_app`` so that
``server/main.py`` / Passenger never import a half-initialized ``app.main``.
"""

from __future__ import annotations

from .factory import create_app

app = create_app()

__all__ = ["app", "create_app"]
