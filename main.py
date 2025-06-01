# This program should:
# On an interval:
# - Check for torrents that are completed
# - If they are completed, (and moved properly)
# - Rsync them to jupiter
# - and add the tag "Done"
# - Such that we're not gonna try and copy them again
#
# Tags:
# - TV_Show
# - Movie
# - Moved
import sys
import subprocess

from qbit_api import QbitInterface, TorrentInfo
from pathlib import Path
from rsync import rsync_copy, RsyncStatus

from config import Config

def main():

    env = Config()
    qbit = QbitInterface(env.qbit_username, env.qbit_password, env.qbit_url)

    all_torrents = qbit.get_downloaded_torrents()

    for torrent in all_torrents:
        tags = qbit.convert_tags_to_array(torrent["tags"])

        # Don't rsync incomplete or already moved torrents
        if env.moved_tag in tags:
            continue

        print(f"Trying to move: {torrent["name"]}")

        torrent_path = torrent["root_path"]

        # Convert torrent_path to be not an absolute path (if it is)
        if torrent_path.startswith("/"):
            torrent_path = torrent_path[1::]

        from_path = f"{env.rsync_from_path_host}:{env.rsync_from_path_prepend}/{torrent_path}"

        to_path = f"{env.rsync_to_path}"

        did_copy = rsync_copy(from_path, to_path)

        if did_copy == RsyncStatus.FAILED:
            print(f"Failed to rsync torrent: {torrent["name"]}")
            continue

        did_add_tag = qbit.append_tag_to_torrent(
            torrent["hash"], env.moved_tag)

        if not did_add_tag:
            print(f"Failed to add tag MOVED to torrent {torrent["name"]}")
            continue

        print(f"Finished moving: {torrent["name"]}")
        sys.exit(1)
    print("Done!")


if __name__ == "__main__":
    main()
