# This program should:
# On an interval:
# - Check for torrents that are completed
# - If they are completed, (and moved properly)
# - Rsync them to a destination
# - and add the moved tag
# - and respect season info

from qbit_api import QbitInterface, TorrentInfo
from rsync import rsync_copy, RsyncStatus
from tv_show_info import get_tv_show_info
from config import Config
from logger import Logger
from ollama import ai_rename, TvShowOrMovie
from typing import Optional
from validation import check_for_case_issues
import time

env = Config()
logger = Logger()


def handle_tv_show(torrent: TorrentInfo) -> bool:
    show_info = get_tv_show_info(torrent["name"])

    if show_info is None:
        logger.warn("Failed to gather tv show info")
        return False
    
    torrent_path = torrent["root_path"]

    if torrent_path.startswith("/"):
        torrent_path = torrent_path[1::]

    from_path = f"{env.rsync_from_path_host}:{env.rsync_from_path_prepend}/{torrent_path}/"

    if show_info.is_multiple:
        to_path = f"{env.rsync_to_path_tv_shows}/{show_info.show_name}"
    else:
        # Only append season info, if there is season info
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


def check_tags(qbit: QbitInterface):
    # Ensure tags
    required_tags = [
        env.tv_show_tag,
        env.moved_tag,
        env.movie_tag,
        env.failed_tag,
        env.ai_tag
    ]

    qbit_tags = qbit.get_all_tags()

    for tag in required_tags:
        if tag not in qbit_tags:
            qbit.create_tag(tag)
            logger.log(f"Adding missing tag to qbittorrent: {tag}")


def handle_ai_tag(torrent: TorrentInfo, tags: set[str]) -> Optional[str]:
    new_torrent_name = None

    did_try_rename = False
    if env.tv_show_tag in tags and not env.movie_tag in tags:
        did_try_rename = True
        new_torrent_name = ai_rename(TvShowOrMovie.TvShow,
                                     torrent["name"])
    elif env.movie_tag in tags and not env.tv_show_tag in tags:
        did_try_rename = True
        new_torrent_name = ai_rename(
            TvShowOrMovie.Movie, torrent["name"])

    if new_torrent_name is None:
        logger.warn(f'Failed to AI Rename {torrent["name"]}, did we try? {did_try_rename}')
        return None

    return new_torrent_name


def main():
    if env.dry_run:
        logger.warn("DRY RUN")

    qbit = QbitInterface(env.qbit_username, env.qbit_password, env.qbit_url)

    check_tags(qbit)

    while True:
        check_for_case_issues(qbit)

        useful_torrents = qbit.get_unmoved_not_failed_torrents()

        did_handle = False
        for torrent in useful_torrents:
            tags = qbit.convert_tags_to_array(torrent["tags"])

            # Don't touch moved or failed torrents
            # if (env.moved_tag or env.failed_tag) in tags:
            # continue

            # Ai Stuff
            if env.ai_tag in tags:
                new_torrent_name = handle_ai_tag(torrent, tags)
                if new_torrent_name is None:
                    did_handle = False
                else:
                    qbit.rename_torrent(torrent, new_torrent_name)
                    # Handle moving on next iteration
                    qbit.remove_tag_from_torrent(torrent["hash"], env.ai_tag)

            # Regular moving
            if env.movie_tag in tags and env.tv_show_tag not in tags:
                did_handle = handle_movie(torrent)
            elif env.tv_show_tag in tags and env.movie_tag not in tags:
                did_handle = handle_tv_show(torrent)
            else:
                # maybe log?
                continue

            # Failure
            if not did_handle:
                logger.warn(f"failed to handle {torrent['name']}")
                qbit.append_tag_to_torrent(torrent, env.failed_tag)
                continue
            qbit.append_tag_to_torrent(torrent, env.moved_tag)
        logger.log("Main loop done")
        time.sleep(600)


if __name__ == "__main__":
    main()
