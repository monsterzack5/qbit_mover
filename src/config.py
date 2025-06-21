from dotenv import load_dotenv
from typing import NoReturn
import os
import sys

# TODO: Don't have the env names in the file twice


def _ensure_expected_env_vars() -> None | NoReturn:
    rc = 0
    rc |= len(os.getenv("QBIT_URL", "")) == 0
    rc |= len(os.getenv("QBIT_USERNAME", "")) == 0
    rc |= len(os.getenv("QBIT_PASSWORD", "")) == 0
    rc |= len(os.getenv("RSYNC_FROM_PATH_PREPEND", "")) == 0
    rc |= len(os.getenv("RSYNC_FROM_PATH_HOST", "")) == 0
    rc |= len(os.getenv("RSYNC_TO_PATH_MOVIES", "")) == 0
    rc |= len(os.getenv("RSYNC_TO_PATH_TV_SHOWS", "")) == 0
    rc |= len(os.getenv("MOVIE_TAG", "")) == 0
    rc |= len(os.getenv("TV_SHOW_TAG", "")) == 0
    rc |= len(os.getenv("MOVED_TAG", "")) == 0
    rc |= len(os.getenv("FAILED_TAG", "")) == 0
    rc |= len(os.getenv("LOG_FILE", "")) == 0

    if rc:
        print("Fatal: Env vars are not correct")
        sys.exit(1)


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            load_dotenv()
            _ensure_expected_env_vars()
            self._initialized = True

    @property
    def qbit_url(self) -> str:
        return os.getenv("QBIT_URL", "")

    @property
    def qbit_username(self) -> str:
        return os.getenv("QBIT_USERNAME", "")

    @property
    def qbit_password(self) -> str:
        return os.getenv("QBIT_PASSWORD", "")

    @property
    def rsync_from_path_prepend(self) -> str:
        return os.getenv("RSYNC_FROM_PATH_PREPEND", "")

    @property
    def rsync_from_path_host(self) -> str:
        return os.getenv("RSYNC_FROM_PATH_HOST", "")

    @property
    def rsync_to_path_movies(self) -> str:
        return os.getenv("RSYNC_TO_PATH_MOVIES", "")

    @property
    def rsync_to_path_tv_shows(self) -> str:
        return os.getenv("RSYNC_TO_PATH_TV_SHOWS", "")

    @property
    def movie_tag(self) -> str:
        return os.getenv("MOVIE_TAG", "")

    @property
    def tv_show_tag(self) -> str:
        return os.getenv("TV_SHOW_TAG", "")

    @property
    def moved_tag(self) -> str:
        return os.getenv("MOVED_TAG", "")

    @property
    def failed_tag(self) -> str:
        return os.getenv("FAILED_TAG", "")

    @property
    def log_file(self) -> str:
        return os.getenv("LOG_FILE", "")

    @property
    def dry_run(self) -> bool:
        dry = os.getenv("DRY_RUN", "")
        if dry.lower() == "true":
            return True
        return False
