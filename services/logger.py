import logging
import os

"""
Application logging configuration.
"""

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    filename="data/app.log",
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)

logger: logging.Logger = logging.getLogger(__name__)