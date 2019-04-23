# -*- coding: utf-8 -*-

#import nltk, re, #pickle #string, 
from nltk.tokenize import RegexpTokenizer
import re
import zlib

def process_srt(srt, verbose = 0, runtime = None):
    """
    Takes an SRT file as string input. Returns a single list of words.
    All punctuation, formatting tags and capitalisation is removed.
    """
    wordbag = []
    tokenizer = RegexpTokenizer(r'\w+')

    lines_list = srt.splitlines()

    N_lines = len(lines_list)

    line = 0
    while True:
        line += 2 # skip the number and timestep

        this_line = lines_list[line]
        while this_line !=  '':  # Collect all of the subtitle text
            if 'http://' not in this_line and 'www' not in this_line:
                cleaned_1 = re.sub('<[^>]*>', '', this_line.lower())  # Remove formatting tags
                cleaned_2 = tokenizer.tokenize(cleaned_1)  # Tokenize and remove punc 
                wordbag += cleaned_2  # Add to word bag

            line += 1  # Move to next line
            if line < N_lines:
                this_line = lines_list[line]
            else:
                break


        while line+2 < N_lines and lines_list[line+1] == '':  # Traverse all blank lines
            line += 1

        # Check for end of file
        if not line+2 < N_lines:
            break

        # Check for end of readable text
        if lines_list[line+1].isdigit() and '-->' in lines_list[line+2]:
            line+=1
        else:
            break 
        
        if runtime is not None:
            # break if over runtime
            if int(lines_list[line+1][3:5]) > runtime:
                break
            
    if verbose == 1:
        print("Done on line " + str(line) + " of " + str(N_lines))
    
    return wordbag


def get_epsiode_ids(episode_metas):
    """
    Creates a list of all IMDB ID for the epsiodes inside 
    of a list of episode metadatas.
    """
    ids = []
    for ep in episode_metas:
        ids.append(ep['imdb_id'])
        
    return ids

    
    
    
def get_episode_metas(series_obj):
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

    for season, episodes in series_obj['episodes'].items():
        for episode, movie_obj in episodes.items():
            epsiode_data = {"season":season, "episode": episode, "imdb_id":movie_obj.movieID, 
                            'title':movie_obj.data['title'], "air_date": movie_obj.data['original air date']}
            all_episodes.append(epsiode_data)
            
    print("Returning", len(all_episodes), " epsiodes.")
    return all_episodes


def load_from_file(ids, data_path = "."):
    """
    Takes an array of ids or single id and loads that srt file and returns
    the srt files in a dictionary with IDs as keys.
    """
    
    if type(ids) is int or type(ids) is str:
        with open(data_path+str(ids)+".srt","r") as f:
            data = f.read()
            return {ids:data}
    elif type(ids) is list:
        all_data = []
        for this_id in ids:
            try:
                with open(data_path+str(this_id)+".srt","r") as f:
                    this_data = f.read()
                all_data.append((this_id,this_data))
            except FileNotFoundError:
                print("There wasn't a file for ", this_id)
        return dict(all_data)
    
    
    
    
def add_srt_to_meta(meta_list, srt_dict):
    """
    Combindes the metadata and srt dictionarys.
    
    :param meta_list A list of metadata dictionarys from get_episode_metas
    :param srt_dict A dictionary of ID, SRT 
    """
    
    new_list = [] # Make a new array to avoid pass my refrence override
    for element in meta_list:
        imdb_id = element['imdb_id']
        new_dict = element.copy() # Copy the dict to avoid PBR override
        if imdb_id in srt_dict:
            new_dict['srt'] = srt_dict[imdb_id]
            new_list.append(new_dict)
    return new_list
    
    
def compress_by_token_ratio(list_of_string):
    """
    Takes a string that has been tokenized and finds the ratio of the 
    compressed data to the uncompressed data.
    
    :param list_of_string A list of ordered string objects to be compressed.
    """
    
    vocab_set = set(list_of_string)
    code_set = set(list(range(1,len(vocab_set)+1)))
    
    # Transforming to integer code 
    
    ref = dict(zip(vocab_set, list(range(1,len(vocab_set)+1))))
    
    coded_list = [ref[tok] for tok in list_of_string]
    
    # Join coded list into single string
    single_string = str(coded_list).encode("utf-8")
        
    return _compress(list_of_string) / len(single_string)

def _compress(list_of_string):
    """
    Internal Compression Method using zlib compression.
        :param list_of_string A list of ordered string objects to be compressed.

    """
    vocab_set = set(list_of_string)
    code_set = set(list(range(1,len(vocab_set)+1)))
    
    # Transforming to integer code 
    
    ref = dict(zip(vocab_set, list(range(1,len(vocab_set)+1))))
    
    coded_list = [ref[tok] for tok in list_of_string]
    
    # Join coded list into single string
    single_string = str(coded_list).encode("utf-8")
    
    # Use zlib to compress
    encoded_string = zlib.compress(single_string)
    
    return len(encoded_string) 

def _hhat(list_of_string):
    """ Non parametric entropy estimator for a single random process. """

    word_set = set(list_of_string)

    ref = dict(zip(word_set, list(range(len(word_set)))))

    data = [ref[w] for w in list_of_string]
    
    N = len(data)
    
    vocab_set = set(data)
        
    # Making Data structure
    
    lookup_table = dict((e,[]) for e in vocab_set)
    
    Lambdas = [1]
    
    for i in range(1,N):
        
        # Add previous to lookup
        lookup_table[data[i-1]]+=[i-1]
        
        
        # Search for lambda_i
        subset_length = 1
        
        valid_targets = lookup_table[data[i]]
        while len(valid_targets) > 0 and i+subset_length < N:
            # Take every valid target, check if next word is valid, make new target set
            valid_targets = [t+1 for t in valid_targets if t+1 in lookup_table[data[i+subset_length]]]
            subset_length += 1
        
        Lambdas += [subset_length]

    return N*math.log(N,2)/sum(Lambdas)

    
def check_sub_format(long_string):
    """ Checks for sub formats instead of SRT formats"""
    if long_string[0] == '{':
        return False
    if long_string[0] == '1' or long_string[0] == '0':
        return True
    print("Not sure, first line is ", long_string.splitlines()[0])
    return False


def normalised_paired_compression(a_string, b_string, method = 'compression'):
    """
    Returns a noramlised paired compression ratio via the formula:
        2 * C(A+B) / (C(A) + C(B))
    """
    if method == 'compression':
        C_AB = _compress(a_string+b_string)
        C_A = _compress(a_string)
        C_B = _compress(b_string)

        return C_AB / (C_A+ C_B)

    elif method == 'entropy':
        C_AB = _hhat(a_string+b_string)
        C_A = _hhat(a_string)
        C_B = _hhat(b_string)

        return C_AB / (C_A+ C_B)

    else:
        raise Exception("Not a valid method")



    
    
    
    
    
    
    
