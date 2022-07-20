import datetime
import pandas as pd
import numpy as np
import berserk
import os
import math
import pytz
import time
import asciichartpy as ac


def data_extractor():
    token = os.environ.get('TOKEN')
    session = berserk.TokenSession(token)
    client = berserk.Client(session=session)
    extract = client.games.export_by_player('YourKingIsInDanger',as_pgn=False, since=None, until=None, 
                                          max=None, vs=None, rated=True, perf_type='blitz', color=None, 
                                          analysed=None, moves=False, tags=False, evals=False, opening=False)
    data = list(extract)
    return data


def dict_formation(data):
    main_dict = {'Played':[], 'My Rating':[], 'Rating Fluctuation':[]}
    data_length = len(data)
    for i in range(data_length):
        if data[i]['players']['white']['user']['id'] == 'yourkingisindanger':
            main_dict['My Rating'].insert(0,data[i]['players']['white']['rating'])
            main_dict['Rating Fluctuation'].insert(0,data[i]['players']['white']['ratingDiff'])
        else:
            main_dict['My Rating'].insert(0,data[i]['players']['black']['rating'])
            main_dict['Rating Fluctuation'].insert(0,data[i]['players']['black']['ratingDiff'])
        main_dict['Played'].insert(0,data[i]['lastMoveAt'].astimezone(pytz.timezone('Asia/Kolkata')))
    return main_dict


def data_formation(main_dict):
    Chess_df = pd.DataFrame.from_dict(main_dict, orient ='columns')
    Chess_df['New Rating'] = Chess_df['My Rating'] + Chess_df['Rating Fluctuation']
    return Chess_df
    
    
def main():
    Chess_df = data_formation(dict_formation(data_extractor()))
    ratings_list = list(Chess_df['New Rating'])[::-1][0:100][::-1]
    return (ac.plot(ratings_list, {'height': 15, 'format':'{:4.0f}'})), ratings_list, \
        list(Chess_df['Played'])[::-1][0].strftime('%a, %d-%b-%Y %I:%M %p %Z')


if __name__ == "__main__":
    plot, rl, date = main()
    print (plot, '\n')
    print('Maximum Rating: {}'.format(max(rl)))
    print('Average Rating: {}'.format(round(np.mean(rl))))
    print('Current Rating: {}'.format(rl[-1]), '\n')
    print('Last Game Played On:',date)
    
