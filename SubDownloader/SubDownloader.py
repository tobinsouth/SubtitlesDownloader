from imdb import IMDb, IMDbError
from pythonopensubtitles.opensubtitles import OpenSubtitles




class SubDownloader(object):
    """ take the name of any TV show or movie, download 
the SRT files and save them"""


    def __init__(self, search_term = None, save_name = None, data_path = "."):
        """
        Initialize the SubDownloader object
            
        """
        self.ost = OpenSubtitles()
        self.ia = IMDb()
        
        self.password_array = []
        self.used_accounts = []
        self.data_path = data_path
        
        self.search_term = search_term
        self.save_name = save_name
        


    def add_login(self, username, password):
        """
        Adds a user account for OpenSubtitles to the list of 
        possible accounts.
        
        Multiple accounts can be added to deal with hitting rate 
        limits in tokens.
        """
        
        if (username, password) in self.password_array:
            print("User already added")
            return -1
        else:
            self.password_array.append((username, password))
        
        
        
    def login(self, username = None, password = None):
        """
        Used to login to OpenSubtitles and collect API token.
        If a username and password are passed then they will be 
        used to login. Else, the previously added logins will 
        be used if they have not already been used in this session.
        """
        
        # If a manual user is passed to function
        if username is not None and password is not None:
            token = self.ost.login(username, password)
            if token is None:
                raise Exception("Failed to collect token from manual pass")
            else:  
                # Add account to list of accounts
                if (username, password) not in self.password_array:
                    self.password_array.append((username, password))
                
                # Add to list of used accounts
                if username not in self.used_accounts:
                        self.used_users.append(username)
                        
        # Automatically login using a user that has not be used before.
        if len(self.password_array) == 0:
            raise Exception("Can't log in with a username and password")
        else:
            for usr, pwd in self.password_array: # Loop through each user
                if usr not in self.used_accounts:  # Check for previous usage
                    
                    token = self.ost.login(usr, pwd)
                    
                    if token is None:
                        raise Exception("Failed to login using a previously unused account")
                    else:
                        self.used_users.append(usr)
                        return True
            print("Reached end of loop through accounts.",
                  "This suggests all accounts have been used.",
                  "Try running rate_limit_clean to address issue.",
                  "Meanwhile, first user has been used.")
            
        usr, pwd = self.password_array[0]
        token = self.ost.login(usr, pwd)
        return token
        
        
    
    def rate_limit_clean(self):
        """
        Manually overides the rate limit avoidance framework. 
        Use if 24 hours have passed as the rate limits will reset.
        """
        self.used_accounts = []
        
        
        
    def remove_usr(self, username):
        """
        Removes a user from the list of possible accounts.
        Use this if something went wrong.
        """
        for i, tup in self.password_array:
            if tup[0] == username:
                del self.password_array[i]

    
    
    def set_data_path(self, path):
        """
        Sets the path that data will be saved at.
        """
        self.data_path = path
        
    
    def set_search_term(self, term):
        """ Sets the search term that will be used to find subtitles"""
        self.search_term = term
        
        
    def set_save_name(self, name= None):
        """
        Sets the save name for the files if given,
        otherwise, sets save to the search term without spaces.
        """
        if name is not None:
            self.save_name = name
            return
        else:
            if self.save_name is not None:
                return
            else:
                self.save_name = self.search_term.replace(" ","")  
                # Potential bug if .replace bcomes an in place operation
                return 
            
    
    def find_series(self, search_term = None, force_series = False):    
        """
        Searchs IMDB for media that matches the seach term. 
        Movies will return an ID.
        TV Series will return the ID of the series but will update metadata 
        to include all episode ID's
        
        :param force_series will force the search to only return tv series.
            This should be used for reliability.
            
        """
        # Dealing with search term
        if search_term is not None:
            self.set_search_term(search_term)
        else:
            if self.search_term is None:
                raise Exception("Can't search for nothing")
                
        
        # Performing Search
        try:
            search_results = self.ia.search_movie(self.search_term)
        except IMDbError as err:
            print("Something went wrong searching IMDB, process aborted.")
            raise err
        
        # Viewing Results
        
        
        for i in range(len(search_results)):  
            # Loop through results until one is a TV series.
            
            result = search_results[i]
            
            if result.data['kind'] == "movie" and not force_series:
                print("Found a movie called", result['title'],
                      "If this not correct, try a different search term",
                      "If you were looking for a series try ",
                      "force_series = True")
                return result
            
            if result.data['kind'] == 'tv series':  # Check if episode, movie, or series
                
                print("The series found was "+result['title'],
                     " If this is not the correct series then try using a different search term.")
                
                # Update to get the episodes
                try:
                    self.ia.update(result, 'episodes')
                except IMDbError as e:
                    print("Something went wrong getting the episodes, process aborted.")
                    raise e  
                
                # If tv series is found and episodes are successfully downloaded then return
                return result
        
        # If the end is reached without finding anything
        raise Exception('Could not find any shows that matched the parameters.')
                
            
            
            
    def get_all_episodes(self, series):
        """
        Creates a list of epsiode information. 
        
        Requires a series object from IMDB with episodes already updated within it.
        
        Returns a list containing a dictionary for each episode.
        Dictionary has the following keys:
            - "season": season number
            - "episode": episode number 
            - "imdb_id": movieID from IMDB, used for further scraping 
            - "title": episode title, 
            - "air_date": original air date
        """
        
        all_episodes = []
    
        for season, episodes in series['episodes'].items():
            for episode, movie_obj in episodes.items():
                epsiode_data = {"season":season, "episode": episode, "imdb_id":movie_obj.movieID, 
                                'title':movie_obj.data['title'], "air_date": movie_obj.data['original air date']}
                all_episodes.append(epsiode_data)
                
        print("Returning", len(all_episodes), " epsiodes.")
        return all_episodes
        
        
        
        
        
        
        
        
        
        
        



