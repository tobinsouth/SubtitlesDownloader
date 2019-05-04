from imdb import IMDb, IMDbError
from pythonopensubtitles.opensubtitles import OpenSubtitles
import os
import pickle


class SubDownloader(object):
    """ 
    take the name of any TV show or movie, download 
    the SRT files and save them
    """

    def __init__(self, search_term = None, data_path = ".", verbose = 2):
        """
        Initialize the SubDownloader object
            
        """
        self.ost = OpenSubtitles()
        self.ia = IMDb()
        
        self.password_array = []
        self.used_accounts = []
        self.data_path = data_path
        self.verbose = verbose
        
        self.search_term = search_term
        
        self.current_account = None
        

    def add_login(self, username, password):
        """
        Adds a user account for OpenSubtitles to the list of 
        possible accounts.
        
        Multiple accounts can be added to deal with hitting rate 
        limits in tokens.
        """
        
        if (username, password) in self.password_array:
            self.ObjPrint("User already added", important = True)
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
                # Save current account 
                self.current_account = username
                # Add account to list of accounts
                if (username, password) not in self.password_array:
                    self.password_array.append((username, password))
                
                # Add to list of used accounts
                if username not in self.used_accounts:
                        self.used_accounts.append(username)
                        
                return token
                        
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
                        # Save current account 
                        self.current_account = usr
                        self.used_accounts.append(usr)
                        return token
            self.ObjPrint(["Reached end of loop through accounts.",
                  "This suggests all accounts have been used.",
                  "Try running rate_limit_clean to address issue.",
                  "Meanwhile, first user has been used."], important = True)

        usr, pwd = self.password_array[0]
        token = self.ost.login(usr, pwd)
        # Save current account 
        self.current_account = usr
        self.used_accounts.append(usr)
        return -1
        
    def get_current_login(self):
        """ Returns current login username """
        return self.current_account
    
    def rate_limit_clean(self):
        """
        Manually overides the rate limit avoidance framework. 
        Use if 24 hours have passed as the rate limits will reset.
        """
        self.used_accounts = []
        
        
    def rate_limit_naughty_fix(self):
        """
        Avoids the rate limit by logining in with a different account.
        """
        return self.login()
        
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
    
            
    
    def find(self, search_term = None, force_series = False):    
        """
        Searchs IMDB for media that matches the seach term. 
        Movies will return a list with the IMDB ID.
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
                self.ObjPrint(["Found a movie called", result['title'],
                      "\n If this not correct, try a different search term.",
                      "\n If you were looking for a series try ",
                      "force_series = True"])
                return result
            
            if result.data['kind'] == 'tv series':  # Check if episode, movie, or series
                
                self.ObjPrint(["The series found was "+result['title'],
                     "\n If this is not the correct series then try using a different search term."])
                
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
                
    def find_from_id_tv_show(self, imdb_id):
        """ Finds the IMDB Object based on a give IMDB ID """
        try:
            result = self.ia.get_movie(imdb_id)
            self.ia.update(result, 'episodes')
        except IMDbError as e:
            print("Something went wrong getting the episodes, process aborted.")
            raise e  

        return result
        
        
        
    def download_opensubtitles(self, imdb_ids, save = False, new_data_path = None):
        """
        Takes some IMDB ID's and downloads the first english subtitle 
        search results as SRT files.
        
        Ideally this function takes all the episode ID's. This allows 
        the program to collect the subtitles 
        in bunches to avoid hitting rate limits. Each call can make 
        20 requests for subtitles in one.
        """
        
        id_subtitles = []
        id_refrence = {}
        
        # Get the subtitles of all of the episodes in the imdb_ids list
        self.ObjPrint("Search for subtitles of all episodes.")
        for imdb_id in imdb_ids:
            databased_search = self.ost.search_subtitles([{'imdbid':imdb_id, 'sublanguageid': 'eng'}])
            try:
                id_subtitle = databased_search[0].get('IDSubtitleFile')
                id_subtitles+= [id_subtitle]
                id_refrence[id_subtitle] = imdb_id
            except IndexError:
                print("Couldn't find any search results for this episode, ",
                      imdb_id, " ~ Will not be downloaded.")
        
        all_subtitles = {}
        
        # We will group ID into batches of 18 to make the call.
        
        self.ObjPrint("Starting subtitle downloads.")
        batchs = []
        mini_list = []
        for an_id in id_subtitles:
            if len(mini_list)<19:
                mini_list+=[an_id]
            else:
                batchs+=[mini_list]
                mini_list = []
        if len(mini_list)>0:
            batchs+=[mini_list]
                
        for mini_list in batchs:
                srt_dict = self.ost.download_subtitles(mini_list, return_decoded_data=True)

                # Check that the download worked
   
                 while srt_dict is None:
                    print("OpenSubtitles returned nothing, possibly due to rate limit",
                          "Attempting to login via a new user")
                    
                    fix_result = self.rate_limit_naughty_fix()
                    
                    if fix_result == -1:
                        raise Exception("Account Access Failed")

                    srt_dict = self.ost.download_subtitles(mini_list, return_decoded_data=True)


                for id_ in mini_list:           
                    all_subtitles[id_]= srt_dict[id_]
                
                self.ObjPrint(["Downloaded SRT for all", mini_list])
                
        
        self.ObjPrint("Finished Downloading")
        # Match the resulted subtitle id to imdb ids for returning
        returnable_dict = {}
        for sub_id, subtitles in all_subtitles.items():
            returnable_dict[id_refrence[sub_id]] = subtitles
            
        if save:
            self.ObjPrint("Saving Files")
            if new_data_path is not None:
                self.data_path = new_data_path
            try:
                if not os.path.exists(self.data_path):
                    os.makedirs(self.data_path)
                for imdb_id, subtitle in returnable_dict.items():
                    with open(self.data_path+imdb_id+".srt", "w+") as f:
                        f.write(subtitle)
                self.ObjPrint("Saved all to file")
            except:
                self.ObjPrint("Somethign went wrong during saving")
            
        return returnable_dict
    
    def ObjPrint(self, obj, important = False):
        if self.verbose > 2:
            print(obj)
        elif self.verbose == 1:
            if important == True:
                print(obj)
        
                
    def save_meta_data(self, meta_data_obj, new_data_path = None):
        """
        Saves the metadata object of the episodes to file as a pickle.
        """
        if new_data_path is not None:
            self.data_path = new_data_path
            
        try:
            if not os.path.exists(self.data_path):
                os.makedirs(self.data_path)
           
            with open(self.data_path+"meta_object.pickle", "wb+") as f:
                pickle.dump(meta_data_obj, f)
                print("File has been saved")
        except:
            self.ObjPrint("Somethign went wrong during saving")
        
        
        
        



