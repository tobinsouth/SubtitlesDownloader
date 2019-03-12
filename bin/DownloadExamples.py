from SubDownloader import SubDownloader
# The SubDownloader object does most of the heavy lifting
import SubDownloader.utils as utl
# The utils contains helpful functions to do work


# Example Downloading Movie
sd = SubDownloader(search_term = "Iron Man", data_path = "./Data/IM") # Creates object

sd.login('tobin.south@adelaide.edu.au', 'movies')

movie_object = sd.find()

movie_id = movie_object.movieID

movie_srt_dict = sd.download_opensubtitles([movie_id], save = False)

movie_srt= movie_srt_dict[movie_id]



# Example Downloading Series
sd = SubDownloader(search_term = "Game of Thrones", data_path = "./Data/GoT/")

sd.login('tobin.south@adelaide.edu.au', 'movies')

sd.add_login('a1704567@adelaide.edu.au', 'movies')


series_object = sd.find(force_series = True)

all_episodes_meta_data = utl.get_episode_metas(series_object)

all_episode_ids = utl.get_epsiode_ids(all_episodes_meta_data)

series_srt_dict = sd.download_opensubtitles(all_episode_ids, save = False)

joined_data = utl.add_srt_to_meta(all_episodes_meta_data, series_srt_dict)



# Example loading in previously downloaded SRT files

sd = SubDownloader()

sd.set_search_term("Game of Thrones")

series= sd.find(force_series = True)

meta_data = utl.get_episode_metas(series)

episode_ids = utl.get_epsiode_ids(meta_data)

data_srt = utl.load_from_file(episode_ids, data_path = "./Data/GoT/")

data = utl.add_srt_to_meta(episode_ids, data_srt)



