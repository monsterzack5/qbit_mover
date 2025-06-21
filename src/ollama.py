import requests
import json

from logger import Logger
from config import Config
from typing import Optional, TypedDict
from enum import Enum

logger = Logger()
env = Config()


class MessageContent(TypedDict):
    new_name: str


class Message(TypedDict):
    role: str
    content: str


class LlamaApiResponse(TypedDict):
    model: str
    created_at: str
    message: Message
    done_reason: str
    done: bool
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


class TvShowOrMovie(Enum):
    TvShow = 1
    Movie = 2

    def __str__(self):
        return self.name


headers = {
    "Content-Type": "application/json"
}

TV_SHOW_SYSTEM_PROMPT = """
You are a AI Agent tasked with renaming titles of tv show files to make the name cleaner and more accurate. You must also add metadata to the end of the title which includes the season number and the episode number if it is available. You must clean the title so all it shows is the tv show name and the metadata, removing the extra characters.

You should use this format for metadata if there is no episode information:
```json
{ "new_name": "{TV SHOW NAME}/S{SEASON NUMBER}" }
```

You should use this format for metadata if there is episode information:
```json
{ "new_name": "{TV SHOW NAME}/S{SEASON NUMBER}E{EPISODE NUMBER}" }
```

For example:
`Best.Show.S07.Complete.1080p.WEBRip.10bit.DDP5.1.x265-HODL`
Should Become
```json
{ "new_name": "Best Show/S07" }
```
and
`Cool Show Season 1 Complete 720p Web-DL x264 [i_c]`
Should Become
```
{ "new_name": "Cool Show/S1" }
```

You should respond in JSON ONLY and ONLY respond with the new_name key. You should leave out any ` characters.
"""
MOVIE_SYSTEM_PROMPT = """
You are a AI Agent tasked with renaming titles of movie files to make the name cleaner and more accurate. If present, you should include the year the movie was released, and if it was a special edition, directors cut, or any other special common qualifier.

For example:
`The.Best.Movie.Ever (2022) (1080p AMZN WEB-DL x265 HEVC 10bit EAC3 5.1) [ZxD]`
Should Become
```json
{ "new_name": "The Best Movie Ever (2022)" }
```
and
`Mad Wealthy People 2018 Directors Cut (1080p BluRay x265 HEVC 10bit AAC 5.1) [DxM]`
Should Become
```
{ "new_name": "Mad Wealthy People (2018) Directors Cut" }
```

You should respond in JSON ONLY and ONLY respond with the new_name key. You should leave out any ` characters.
"""


def ai_rename(content_type: TvShowOrMovie, torrent_name: str) -> Optional[str]:
    payload = {
        "model": "llama3.1",
        "messages": [
            {
                "role": "system",
                "content": TV_SHOW_SYSTEM_PROMPT if content_type == TvShowOrMovie.TvShow else MOVIE_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": torrent_name
            },
        ],
        "stream": False
    }

    logger.log(f"Running llama3.1, type = {content_type}")

    resp = requests.post(env.ollama_url, json=payload, headers=headers)

    if resp.status_code != 200:
        logger.warn(
            f"Ollama called failed with status code: {resp.status_code}")
        return None
    try:
        resp_data: LlamaApiResponse = resp.json()
    except:
        return None

    content = resp_data.get("message", None).get("content", None)
    try:
        new_name = json.loads(content)
    except:
        return None

    return new_name.get("new_name", None)
