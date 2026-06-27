"""Tiny logging helper used across the OrderTrack API.

Configures the ROOT logger with a file + stream handler. Attaching to the root
(rather than to each named logger) means every logger in the process — our own
modules *and* Flask / werkzeug / SQLAlchemy — propagates here, so uncaught
exceptions and 500s land in ``logs/app.log`` too, not just our explicit calls.
"""
import logging
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)

_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _configure_root():
    """Attach our handlers to the root logger once (idempotent under reloads)."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    have_file = any(
        isinstance(h, logging.FileHandler)
        and getattr(h, "baseFilename", None) == LOG_FILE
        for h in root.handlers
    )
    if not have_file:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(_formatter)
        root.addHandler(file_handler)

    have_stream = any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in root.handlers
    )
    if not have_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(_formatter)
        root.addHandler(stream_handler)


_configure_root()


def get_logger(name="ordertrack"):
    """Return a named logger that propagates to the configured root handlers."""
    return logging.getLogger(name)
