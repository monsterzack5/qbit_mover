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
    
Cool Show S02E01 The 1st Episode/S01E01 (contains) ./S01E01.The.1st.Episode.mp4
Cool Show S02E02 The 2ndst Episode/S01E02 (contains) ./S01E02.The.2ndst.Episode.mp4
Cool Show S02E03 The 3ndstest Episode/S01E03 (contains) ./S01E03.The.3ndstest.Episode.mp4

```

## Tags
- TV_Show
- Movie
- Moved
- Failed

The torrent must have a `TV_Show` or `Movie` tag, or else it will be ignored. After a torrent has been renamed/organized and moved, it gets the `Moved` tag, where it will be ignored from then on, as it should be finished.

