from typing import Optional


class EpisodeInfo:
    def __init__(self, show_name: str, season: str, episode: str):
        self.show_name = show_name
        self.season = season
        self.episode = episode

    def __repr__(self):
        return f"EpisodeInfo(show_name={self.show_name}, season={self.season}, episode={self.episode})"

    def __eq__(self, other):
        if not isinstance(other, EpisodeInfo):
            return False
        return (self.show_name == other.show_name and
                self.season == other.season and
                self.episode == other.episode)


def get_tv_show_info(name: str) -> Optional[EpisodeInfo]:

    def get_leading_digit_count(s: str) -> int:
        count = 0
        while count < len(s) and s[count].isdigit() and count <= 3:
            count += 1
        return count

    split = name.split("/")

    if len(split) != 2 or not split[1].lower().startswith("s"):
        return None

    info = split[1].lower()

    season_digits = get_leading_digit_count(info[1:])

    season = info[1:season_digits + 1]

    if len(season) == 0:
        return None

    if len(info) == len(season) + 1:
        return EpisodeInfo(split[0], season, "")

    if info[season_digits + 1] != "e":
        print("next char is not e")
        return None

    season_info_offset = len(season) + 1

    episode_digits = get_leading_digit_count(info[season_info_offset + 1:])

    episode = info[season_info_offset +
                   1:season_info_offset + 1 + episode_digits]

    if len(season) + len(episode) + 2 != len(info):
        # Extra data after E000...
        return None

    return EpisodeInfo(split[0], season, episode)
