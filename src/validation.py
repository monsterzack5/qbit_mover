from logger import Logger
from config import Config
from qbit_api import TorrentInfo, QbitInterface
from tv_show_info import get_tv_show_info
logger = Logger()
env = Config()


class RenameInfo:
    new_name: str
    torrent_info: TorrentInfo

    def __init__(self, new_name: str, torrent_info: TorrentInfo) -> None:
        self.new_name = new_name
        self.torrent_info = torrent_info

    def __repr__(self) -> str:
        return f"RenameInfo(new_name='{self.new_name}', torrent_info='{self.torrent_info}')')"


def _check_for_duplicates(all_torrents: list[TorrentInfo]) -> list[RenameInfo]:
    needs_rename: list[RenameInfo] = []
    torrent_map: dict[str, TorrentInfo] = {}
    for elm in all_torrents:
        current_show = get_tv_show_info(elm["name"])
        if current_show is None:
            # failed
            continue

        name_lowercase = current_show.show_name.lower()
        if name_lowercase in torrent_map.keys():
            prev_torrent = torrent_map.get(name_lowercase)
            if prev_torrent is None:
                # an odd edge case
                logger.error(
                    "Failed to capture duplicate torrent and rename")
                continue

            prev_show_info = get_tv_show_info(prev_torrent["name"])

            if prev_show_info is None:
                continue

            if prev_show_info.show_name != current_show.show_name:
                new_name = f"{prev_show_info.show_name}/{current_show.serialize()}"
                needs_rename.append((RenameInfo(new_name, elm)))
                continue
        torrent_map[name_lowercase] = elm
    return needs_rename


def check_for_case_issues(qbit: QbitInterface):
    all_torrents = qbit.get_all_torrents()
    tv_show_torrents = [
        elm for elm in all_torrents if env.tv_show_tag in elm["tags"]]

    torrents_needing_rename = _check_for_duplicates(tv_show_torrents)

    for torrent in torrents_needing_rename:
        logger.warn(
            f"Found capitalization error: {torrent.torrent_info["name"]} is being corrected to: {torrent.new_name}"
        )
        qbit.rename_torrent(torrent.torrent_info, torrent.new_name)
