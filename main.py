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

from qbit_api import QbitInterface, TorrentInfo
from pathlib import Path
from rsync import rsync_copy, RsyncStatus
from tv_show_info import get_tv_show_info, EpisodeInfo
from config import Config

env = Config()


def handle_tv_show(qbit: QbitInterface, torrent: TorrentInfo) -> bool:
    show_info = get_tv_show_info(torrent["name"])

    if show_info is None:
        return False

    torrent_path = torrent["root_path"]

    # Convert torrent_path to be not an absolute path (if it is)
    if torrent_path.startswith("/"):
        torrent_path = torrent_path[1::]


    # Transfer the contents of the torrent into the specified SEASON

    print(f"env: {env.rsync_from_path_prepend}")
    print(f"path: {torrent_path}")

    from_path = f"{env.rsync_from_path_host}:{env.rsync_from_path_prepend}/{torrent_path}/"
    to_path = f"{env.rsync_to_path}/{show_info.show_name}/S{show_info.season}"

    did_copy = rsync_copy(from_path, to_path)

    if not did_copy:
        return False
    return True


def main():

    # should validate env

    if env.dry_run:
        print("DRY RUN")

    qbit = QbitInterface(env.qbit_username, env.qbit_password, env.qbit_url)

    while True:

        tv_shows = qbit.get_unmoved_not_failed_tv_shows()

        print(f"{len(tv_shows)}")

        # The "name" field contains the metadata
        # 1. Verify /S000 is present, if not fail.
        #
        for torrent in tv_shows:
            # Should contain info like:
            # A Cool Show/S01 or /S01E05
            # Focus on the S01
            did_handle = handle_tv_show(qbit, torrent)

            if not did_handle:
                qbit.append_tag_to_torrent(torrent["hash"], env.failed_tag)
                continue
            qbit.append_tag_to_torrent(torrent["hash"], env.moved_tag)

        break

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
