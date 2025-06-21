
from config import Config
import datetime

env = Config()


class Logger:
    _instance = None
    _log_file = None

    COLOR_BLUE = "\x1b[34m"
    COLOR_YELLOW = "\x1b[33m"
    COLOR_RED = "\x1b[31m"
    COLOR_RESET = "\x1b[0m"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            if env.log_file:
                self._log_file = open(env.log_file, "a")
            self._initialized = True

            # setup logger

    @staticmethod
    def __timestamp():
        # they were smoking the good stuff when they made it datetime.datetime
        return datetime.datetime.now().strftime("[%Y-%m-%d - %I:%M:%S %p]")

    def write_to_log(self, message: str):
        if self._log_file is not None:
            self._log_file.write(message)

    def log(self, message: str):
        log_text = f"{self.__timestamp()} LOG: {message}"
        print(f"{self.COLOR_BLUE}{log_text}{self.COLOR_RESET}")
        self.write_to_log(f"{log_text}\n")

    def warn(self, message: str):
        log_text = f"{self.__timestamp()} WARN: {message}"
        print(f"{self.COLOR_YELLOW}{log_text}{self.COLOR_RESET}")
        self.write_to_log(f"{log_text}\n")

    def error(self, message: str):
        log_text = f"{self.__timestamp()} ERROR: {message}"
        print(f"{self.COLOR_RED}{log_text}{self.COLOR_RESET}")
        self.write_to_log(f"{log_text}\n")
