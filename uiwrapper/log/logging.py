import logging
import threading
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
FILE_NAME = "uiwrapper.log"
BACKUP_COUNT = 5
MAX_BYTES = 150 * 1024 * 1024


class Logger:
    """
    A singleton Logger class to handle logging across an application.
    Supports logging to console and file with rotating file handler,
    """

    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def get_logger(name="root"):
        """
        Static method to fetch the singleton instance of the Logger.

            :param name (str): The name of the logger. Defaults to 'root'.
            :returns Logger: The singleton Logger instance.
        """
        if Logger._instance is None:
            with Logger._lock:
                if Logger._instance is None:
                    Logger._instance = Logger(name)
        return Logger._instance

    def __init__(self, name):
        """
        Private constructor for the Logger class.
        This ensures only one instance of the Logger is created.
        :param: name (str): The name of the logger.
        """
        if Logger._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Logger._instance = self

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._setup_console_handler()
        self._setup_file_handler()

    def _setup_console_handler(self):
        """
        Sets up the console handler for the logger with DEBUG level
        and a specific format.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(
        self, log_file=FILE_NAME, max_bytes=MAX_BYTES, backup_count=BACKUP_COUNT
    ):
        """
        Sets up the file handler with rotation for the logger with DEBUG level
        and a specific format.

            :param log_file (str): The name of the log file. Defaults to 'uiwrapper.log'.
            :param max_bytes (int): The maximum file size in bytes before rotation. Defaults to 5MB.
            :param backup_count (int): The number of backup files to keep. Defaults to 5.
        """
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
