import logging
from datetime import datetime
import os

logger_file = f"swimtracker-{datetime.now().strftime('%m-%d-%Y-%H:%M')}.log"

log_dir = "logs"  # Or specify an absolute path like "/var/log/my_app"
log_filepath = os.path.join(log_dir, logger_file)

# Create the log directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Configure the logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)  # Set the desired logging level (e.g., INFO, DEBUG, WARNING)

# Create a file handler
file_handler = logging.FileHandler(log_filepath)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
LOGGER.addHandler(file_handler)

