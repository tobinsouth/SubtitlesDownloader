
# Subtitle Downloader


Subtitle Downloader provides utilties to download subtitles of movies and 
tv shows. You might find it most useful for analysis of tv show or movie text
corpuses. Typical usage often looks like this::

```
    #!/usr/bin/env python
    
    from SubDownloader import SubDownloader
    import SubDownloader.utils as utl
    
    sd = SubDownloader.SubDownloader(search_term = "Iron Man", data_path = "./Data/IM") 
    
    sd.login('username', 'password')
    
    movie_object = sd.find()
    
    movie_id = movie_object.movieID
    
    movie_srt_dict = sd.download_opensubtitles([movie_id], save = False)
    
    movie_srt= movie_srt_dict[movie_id]
```

## Dependencies 


Subtitle Downloader has two main dependencies:

* **IMDbPy** for IMDB scraping::
```
    https://github.com/alberanid/imdbpy
```
```   
    pip install imdbpy
```
* **python-opensubtitles** for accessing Open Subtitles database::
```
    https://github.com/agonzalezro/python-opensubtitles
```
```
    pip install -e git+https://github.com/agonzalezro/python-opensubtitles#egg=python-opensubtitles
```


## Installation

```
pip install -e git+https://github.com/tobinsouth/SubtitlesDownloader#egg=SubtitlesDownloader
```
