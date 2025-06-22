import subprocess
from enum import Enum
from config import Config
from logger import Logger
# TODO: Maybe this should use the env instead of us needing to add the paths?

env = Config()
logger = Logger()


class RsyncStatus(Enum):
    FINISHED = 1
    FAILED = 2


def rsync_copy(from_str: str, to_str: str) -> RsyncStatus:
    # Add quotes just to be sure
    command = ["rsync", f"-aqs", "--mkpath",
               f"{from_str}", f"{to_str}"]

    logger.log(f"rsync command: {' '.join(command)}")

    rc = __cmd_run(command)
    if rc == 0:
        return RsyncStatus.FINISHED
    return RsyncStatus.FAILED


def __cmd_run(command: list[str]) -> int:
    if env.dry_run:
        return 0

    rc = subprocess.run(command, shell=False)
    return rc.returncode
