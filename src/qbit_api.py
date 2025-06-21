import requests

# Union might be needed if fields can be optional or have multiple types
from typing import TypedDict, List, Union
from config import Config
from logger import Logger
from urllib.parse import urlencode

logger = Logger()
env = Config()


class TorrentInfo(TypedDict):
    added_on: int
    amount_left: int
    auto_tmm: bool
    # Or float, if it can be fractional. Given -1, int seems likely.
    availability: int
    category: str
    comment: str
    completed: int
    completion_on: int
    content_path: str
    dl_limit: int
    dlspeed: int
    download_path: str
    downloaded: int
    downloaded_session: int
    eta: int
    f_l_piece_prio: bool
    force_start: bool
    has_metadata: bool
    hash: str
    inactive_seeding_time_limit: int
    infohash_v1: str
    infohash_v2: str  # This is empty in the example, but likely a string
    last_activity: int
    magnet_uri: str
    max_inactive_seeding_time: int
    # Or float, if it can be fractional. Given -1, int seems likely.
    max_ratio: int
    max_seeding_time: int
    name: str
    num_complete: int
    num_incomplete: int
    num_leechs: int
    num_seeds: int
    popularity: float
    priority: int
    private: bool
    progress: float  # Could also be int if it's always 0 or 1, but float is safer for progress
    ratio: float
    ratio_limit: int  # Or float
    reannounce: int
    root_path: str
    save_path: str
    seeding_time: int
    seeding_time_limit: int
    seen_complete: int
    seq_dl: bool
    size: int
    state: str
    super_seeding: bool
    # Assuming tags are a single string; if it could be a list of strings, use List[str]
    tags: str
    time_active: int
    total_size: int
    tracker: str
    trackers_count: int
    up_limit: int
    uploaded: int
    uploaded_session: int
    upspeed: int


class QbitInterface:

    __cookies = {}
    __base_url = ""
    header_plain = {"Content-Type": "text/plain; charset=UTF-8"}
    header_url_encoded = {"Content-Type": "application/x-www-form-urlencoded"}
    env = Config()

    def __init__(self, username: str, password: str, base_url: str):

        self.__base_url = base_url
        self.__authenticate(username, password)

    def __get(self, endpoint, headers={}) -> requests.Response:
        url = f"{self.__base_url}{endpoint}"

        resp = requests.get(url, headers=headers, cookies=self.__cookies)

        if resp.status_code != 200:
            logger.warn(
                f"Warning: Status code != 200, Get: {url} Status Code: ${resp.status_code}")
        return resp

    def __post(self, endpoint, headers={}, payload={}) -> requests.Response:
        url = f"{self.__base_url}{endpoint}"
        resp = requests.post(f"{self.__base_url}{endpoint}",
                             headers=headers, data=payload, cookies=self.__cookies)

        if resp.status_code != 200:
            logger.warn(
                f"Warning: Status code != 200, Post: {url} Status Code: {resp.status_code}")
        return resp

    def __authenticate(self, username: str, password: str):
        payload = {
            "username": username,
            "password": password
        }

        resp = self.__post("/api/v2/auth/login", {}, payload)

        for header, value in resp.headers.items():
            if header == "set-cookie":
                auth_key = value.split(";")[0]
                logger.log(f"Session key is: {auth_key}")
                self.__cookies = {"SID": auth_key.split("=")[1]}
                break

    def get_unmoved_not_failed_torrents(self):
        torrents = self.get_downloaded_torrents()

        filtered: List[TorrentInfo] = []

        for torrent in torrents:
            all_tags = self.convert_tags_to_array(torrent["tags"])
            if not self.env.moved_tag in all_tags and not self.env.failed_tag in all_tags:
                filtered.append(torrent)

        return filtered

    def get_all_torrents(self) -> List[TorrentInfo]:
        # /api/v2/torrents/info
        return self.__get("/api/v2/torrents/info").json()

    @staticmethod
    def convert_tags_to_array(tags: str) -> set[str]:
        # Convert "A,B,C" to { A, B, C }
        all_tags = set()
        for tag in tags.split(","):
            all_tags.add(tag.strip())

        return all_tags

    def get_all_tags(self) -> List[str]:
        # /api/v2/tags
        return self.__get("/api/v2/torrents/tags").json()

    def create_tag(self, new_tag: str):
        payload = f"tags={new_tag}"
        if env.dry_run:
            return
        logger.log(f"Creating tag: {new_tag} in qbittorrent")
        self.__post("/api/v2/torrents/createTags",
                    self.header_url_encoded, payload)

    def rename_torrent(self, torrent: TorrentInfo, new_name: str):
        payload = {
            "hash": torrent["hash"],
            "name": new_name
        }
        encoded_payload = urlencode(payload)

        logger.log(f"Renaming \"{torrent["name"]}\" to \"{new_name}\"")

        if env.dry_run:
            return
        self.__post("/api/v2/torrents/rename",
                    self.header_url_encoded, encoded_payload)

    def append_tag_to_torrent(self, torrent: TorrentInfo, tag: str) -> bool:
        # /api/v2/torrents/addTags
        # hashes=8c212779b4abde7c6bc608063a0d008b7e40ce32|284b83c9c7935002391129fd97f43db5d7cc2ba0&tags=TagName1,TagName2

        payload = {
            "hashes": torrent["hash"],
            "tags":   tag
        }

        if env.dry_run:
            return True

        encoded_payload = urlencode(payload)

        logger.log(f"Adding {tag} to {torrent["name"]}")

        rc = self.__post("/api/v2/torrents/addTags",
                         self.header_url_encoded, encoded_payload)

        return rc.status_code == 200

    def remove_tag_from_torrent(self, torrent_hash: str, tag: str) -> bool:
        payload = {
            "hashes": torrent_hash,
            "tags": tag
        }

        if env.dry_run:
            return True

        encoded_payload = urlencode(payload)

        rc = self.__post("/api/v2/torrents/removeTags",
                         self.header_url_encoded, encoded_payload)

    def get_downloaded_torrents(self) -> List[TorrentInfo]:
        all_torrents = self.get_all_torrents()

        downloaded_torrents = []
        bad_state = set(["stalledDL", "downloading", "metaDL", "error",
                        "moving", "checkingResumeData", "missingFiles", "unknown"])
        for torrent in all_torrents:
            if torrent["state"] not in bad_state:
                downloaded_torrents.append(torrent)
        return downloaded_torrents
