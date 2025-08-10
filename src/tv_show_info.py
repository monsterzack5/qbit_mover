from typing import Optional
from logger import Logger

logger = Logger()


class EpisodeInfo:
    def __init__(self, show_name: str, season: str, episode: str):
        self.show_name = show_name
        self.season = season
        self.episode = episode

        self.is_multiple = False

    def __repr__(self):
        return f"EpisodeInfo(show_name={self.show_name}, season={self.season}, episode={self.episode})"

    def __eq__(self, other):
        if not isinstance(other, EpisodeInfo):
            return False
        return (self.show_name == other.show_name and
                self.season == other.season and
                self.episode == other.episode and
                self.is_multiple == other.is_multiple)

    def serialize(self) -> str:
        ret = ""
        ret += f"{self.show_name} "
        
        if self.is_multiple:
            return ret

        ret += f"S{self.season}"
        if len(self.episode) > 0:
            ret += f"E{self.episode}"
        return ret
    
    def serialize_season_episode_info(self) -> str:
        ret = ""
        ret += f"S{self.season}"
        if len(self.episode) > 0:
            ret += f"E{self.episode}"
        return ret
    
def get_tv_show_info(name: str) -> Optional[EpisodeInfo]:

    def get_leading_digit_count(s: str) -> int:
        count = 0
        while count < len(s) and s[count].isdigit() and count <= 3:
            count += 1
        return count

    split = name.split("/")

    if len(split) != 2:
        logger.warn(f"Failed to parse tv show name: {split}")
        return None

    if split[1] == "Multiple":
        # Contains multiple seasons, only handle the base name
        info  = EpisodeInfo(split[0], "", "")
        info.is_multiple = True
        return info

    if not split[1].lower().startswith("s"):
        logger.error(f"Cannot parse tv show info from: {''.join(split)}")
        return None

    info = split[1].lower()

    season_digits = get_leading_digit_count(info[1:])

    season = info[1:season_digits + 1]

    if len(season) == 0:
        logger.error(f"Failed to grab season info, info: {info}")
        return None

    if len(info) == len(season) + 1:
        return _normalize(EpisodeInfo(split[0], season, ""))

    if info[season_digits + 1] != "e":
        logger.error(f"Failed to grab episode info, info: {info}")
        return None

    season_info_offset = len(season) + 1

    episode_digits = get_leading_digit_count(info[season_info_offset + 1:])

    episode = info[season_info_offset +
                   1:season_info_offset + 1 + episode_digits]

    if len(season) + len(episode) + 2 != len(info):
        # Extra data after E000...
        logger.error(f"Unknown extra data after delimiter: {info} ")
        return None

    return _normalize(EpisodeInfo(split[0], season, episode))


def _normalize(info: EpisodeInfo) -> EpisodeInfo:
    def norm(num: int) -> str:
        if num <= 9:
            return f"0{num}"
        else:
            return f"{num}"

    new_season = f"{norm(int(info.season))}"
    new_episode = info.episode
    if len(info.episode) > 0:
        new_episode = f"{norm(int(info.episode))}"

    return EpisodeInfo(info.show_name, new_season, new_episode)
