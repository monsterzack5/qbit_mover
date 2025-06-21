# This program should:
# On an interval:
# - Check for torrents that are completed
# - If they are completed, (and moved properly)
# - Rsync them to a destination
# - and add the moved tag
# - and respect season info

from qbit_api import QbitInterface, TorrentInfo
from pathlib import Path
from rsync import rsync_copy, RsyncStatus
from tv_show_info import get_tv_show_info, EpisodeInfo
from config import Config
from logger import Logger
import time

env = Config()
logger = Logger()


def handle_tv_show(torrent: TorrentInfo) -> bool:
    show_info = get_tv_show_info(torrent["name"])

    if show_info is None:
        return False

    torrent_path = torrent["root_path"]

    if torrent_path.startswith("/"):
        torrent_path = torrent_path[1::]

    from_path = f"{env.rsync_from_path_host}:{env.rsync_from_path_prepend}/{torrent_path}/"
    to_path = f"{env.rsync_to_path_tv_shows}/{show_info.show_name}/S{show_info.season}"

    did_copy = rsync_copy(from_path, to_path)

    if not did_copy:
        logger.warn(f"Failed to rsync tv_show |{from_path}| to |{to_path}|")
        return False
    return True


def handle_movie(torrent: TorrentInfo) -> bool:

    torrent_path = torrent["root_path"]

    if torrent_path.startswith("/"):
        torrent_path = torrent_path[1::]

    from_path = f"{env.rsync_from_path_host}:{env.rsync_from_path_prepend}/{torrent_path}"
    to_path = f"{env.rsync_to_path_movies}"

    did_copy = rsync_copy(from_path, to_path)

    if did_copy == RsyncStatus.FAILED:
        logger.warn(f"Failed to rsync movie |{from_path}| to |{to_path}|")
        return False

    return True


def main():
    if env.dry_run:
        logger.warn("DRY RUN")

    qbit = QbitInterface(env.qbit_username, env.qbit_password, env.qbit_url)

    while True:

        all_torrents = qbit.get_unmoved_not_failed_torrents()

        for torrent in all_torrents:
            tags = qbit.convert_tags_to_array(torrent["tags"])

            did_handle = False

            if env.movie_tag in tags and not env.tv_show_tag in tags:
                did_handle = handle_movie(torrent)
            elif env.tv_show_tag in tags and not env.movie_tag in tags:
                did_handle = handle_tv_show(torrent)

            if not did_handle:
                qbit.append_tag_to_torrent(torrent["hash"], env.failed_tag)
                continue
            qbit.append_tag_to_torrent(torrent["hash"], env.moved_tag)

        time.sleep(600)


if __name__ == "__main__":
    main()
