import logging
import psutil


class LoggerManager:
    def __init__(self, log_file, log_level=logging.INFO, log_format=None):
        """
        Initializes the LoggerManager for a single log file with multiple loggers.

        :param log_file: Path to the log file where all logs are written.
        :param log_level: Logging level (e.g., logging.DEBUG, logging.INFO).
        :param log_format: Custom log format. If None, a default format is used.
        """
        self.loggers = {}
        self.log_file = log_file
        self.log_level = log_level

        if log_format is None:
            self.log_format = '%(asctime)s - %(name)s - %(levelname)s - CPU: %(cpu_percent)s%% - RAM: %(ram_percent)s%% - %(message)s'
        else:
            self.log_format = log_format

    def get_logger(self, logger_name):
        """
        Returns a logger instance with the specified name, writing to the same log file.

        :param logger_name: Name of the logger.
        :return: Configured logger object.
        """
        if logger_name in self.loggers:
            return self.loggers[logger_name]

        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        formatter = CustomFormatter(self.log_format)

        # Create console handler for all loggers
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Create a single file handler for all loggers
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        self.loggers[logger_name] = logger
        return logger

    def set_log_level(self, log_level):
        """
        Sets the logging level for all loggers.

        :param log_level: New logging level (e.g., logging.DEBUG, logging.INFO).
        """
        for logger in self.loggers.values():
            logger.setLevel(log_level)


# Custom formatter class to include CPU and RAM usage
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.cpu_percent = psutil.cpu_percent(interval=None)
        record.ram_percent = psutil.virtual_memory().percent
        return super().format(record)
