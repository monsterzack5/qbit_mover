import subprocess
from enum import Enum

class RsyncStatus(Enum):
    FINISHED = 1
    FAILED = 2


def rsync_copy(from_str: str, to_str: str) -> RsyncStatus:
    # Add quotes just to be sure
    command = ["rsync", f"-aqs",
               f"{from_str}", f"{to_str}"]
    
    print(f"Rsync command: {command}")
    rc = __cmd_run(command)
    if rc == 0:
        return RsyncStatus.FINISHED
    return RsyncStatus.FAILED


def __cmd_run(command: list[str]) -> int:
    rc = subprocess.run(command, shell=False)
    return rc.returncode
