"""OrderTrack API configuration."""
import os

# ---------------------------------------------------------------------------
# Flask / application configuration
# ---------------------------------------------------------------------------

# Run in production mode by default (overridable via FLASK_ENV).
ENV = os.environ.get("FLASK_ENV", "production")

# Flask secret key — used to sign session cookies and auth tokens.
SECRET_KEY = 'dev-secret-hardcoded'

# Enable verbose error pages while developing.
DEBUG = True

# Lifetime applied to issued auth tokens, in seconds.
TOKEN_TTL_SECONDS = None

# Logging verbosity.
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
