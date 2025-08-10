# qbit_fun (Rename pending)

Moves and reorganizes linux ISOs with special handling for movies and tv show seasons.

## Naming
Torrents should be renamed before being given a `TV_Show` or `Movie` tag. Movie names should be cleaned, but otherwise have no special handling. TV Show names should be cleaned, and then have their season / episode appended onto the end such as: `/S01` or `/S01E05`. Tv shows will be transferred using that metadata. For example:

On Qbit:
```
Cool Show S01/S01
    (contains) -> ./S01.E01.First.Episode.mp4
    (contains) -> ./S01.E02.Second.Episode.mp4
    (contains) -> ./S01.E03.Third.Episode.mp4
Cool Show S02E01 The 1st Episode/S01E01 (contains) ./S02E01.The.1st.Episode.mp4
Cool Show S02E02 The 2ndst Episode/S01E02 (contains) ./S02E02.The.2ndst.Episode.mp4
Cool Show S02E03 The 3ndstest Episode/S01E03 (contains) ./S02E03.The.3ndstest.Episode.mp4
```

On Filesystem, after being transferred:
```

Cool Show
    (contains) -> S01
            (contains) -> ./S01.E01.First.Episode.mp4
            (contains) -> ./S01.E02.Second.Episode.mp4
            (contains) -> ./S01.E03.Third.Episode.mp4
    (contains) -> S02
            (contains) -> ./S02E01.The.1st.Episode.mp4
            (contains) -> ./S02E02.The.2ndst.Episode.mp4
            (contains) -> ./S02E03.The.3ndstest.Episode.mp4
```


## AI Naming
Both TV Shows and Movies can be automatically named using AI, this is done using Mistral 7B via Ollama, which I've found has always given acceptable results. To ask AI to rename your torrent, append the "AI" tag. The prompt tries to get the show title cleaned, removing any unnecessary bits of information but maintaining anything important.

For movies, it tries to keep the year and special condition tags in the title, such as "Directors Cut". 
For TV Shows:
    - For single seasons: it should properly append /S** to the name
    - For multiple seasons: it should append /Multiple to the name
    - For single episodes: it should append /S\**E** to the title

## Using
The torrent must have a `TV_Show` or `Movie` tag, or else it will be ignored. After a torrent has been renamed/organized and moved, it gets the `Moved` tag, where it will be ignored from then on, as it should be finished.

