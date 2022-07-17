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
                                          max=None, vs=None, rated=True, perf_type=None, color=None, 
                                          analysed=None, moves=True, tags=True, evals=False, opening=True)
    data = list(extract)
    return data

def dict_formation(data):
    main_dict = {'Played':[], 'Date':[], 'Time': [], 'Game Type':[] ,'Time Control':[], 'No. of Moves': [],
               'My Rating':[], 'Oponent Rating':[], 'Rating Fluctuation':[], 'My Color':[],
               'Opening':[],'Status':[], 'Winner':[]}
    data_length = len(data)
    for i in range(data_length):
        if data[i]['players']['white']['user']['id'] == 'yourkingisindanger':
            main_dict['My Rating'].insert(0,data[i]['players']['white']['rating'])
            main_dict['Rating Fluctuation'].insert(0,data[i]['players']['white']['ratingDiff'])
            main_dict['Oponent Rating'].insert(0,data[i]['players']['black']['rating'])
            main_dict['My Color'].insert(0,'White')
        else:
            main_dict['My Rating'].insert(0,data[i]['players']['black']['rating'])
            main_dict['Rating Fluctuation'].insert(0,data[i]['players']['black']['ratingDiff'])
            main_dict['Oponent Rating'].insert(0,data[i]['players']['white']['rating'])
            main_dict['My Color'].insert(0,'Black')
        main_dict['Game Type'].insert(0,data[i]['perf'])
        main_dict['No. of Moves'].insert(0,math.ceil(len(data[i]['moves'].split(' '))/2))
        main_dict['Played'].insert(0,data[i]['createdAt'].astimezone(pytz.timezone('Asia/Kolkata')))
        main_dict['Date'].insert(0,data[i]['createdAt'].astimezone(pytz.timezone('Asia/Kolkata')).date())
        main_dict['Time'].insert(0,data[i]['createdAt'].astimezone(pytz.timezone('Asia/Kolkata')).time())
        main_dict['Status'].insert(0,data[i]['status'])
        main_dict['Time Control'].insert(0,'{} Min + {} Sec'.format(data[i]['clock']['initial']//60,
                                                                    data[i]['clock']['increment']))
        try:
            main_dict['Opening'].insert(0,data[i]['opening']['name'])
        except:
            main_dict['Opening'].insert(0,data[i]['initialFen'])
        try:
            main_dict['Winner'].insert(0,data[i]['winner'].capitalize())
        except:
            main_dict['Winner'].insert(0,None)
 
    return main_dict

def data_formation(main_dict):
    raw_df = pd.DataFrame.from_dict(main_dict, orient ='columns')
    Chess_df = raw_df[((raw_df['Game Type'] == 'blitz') | 
                       (raw_df['Game Type'] == 'rapid') | 
                       (raw_df['Game Type'] == 'bullet'))].copy()
    ## Result
    Chess_df.loc[Chess_df['My Color'] == Chess_df['Winner'], 'Result'] = "Won"
    Chess_df.loc[~(Chess_df['My Color'] == Chess_df['Winner']), 'Result'] = 'Lose'
    Chess_df.loc[Chess_df['Winner'].isna(), 'Result'] = 'Draw'

    ## Rating Difference
    Chess_df['Rating Difference'] = Chess_df['Oponent Rating'] - Chess_df['My Rating']

    ## New Rating
    Chess_df['New Rating'] = Chess_df['My Rating'] + Chess_df['Rating Fluctuation']
    Chess_df['Game Type'] = Chess_df['Game Type'].str.capitalize()
    Chess_df['Status'] = Chess_df['Status'].str.capitalize()
    
    return Chess_df
    


def main():
    Chess_df = data_formation(dict_formation(data_extractor()))
    ratings_list = list(Chess_df[Chess_df['Game Type'] == 'Blitz']['New Rating'])[::-1][0:100][::-1]
    return (ac.plot(ratings_list, {'height': 15, 'format':'{:4.0f}'})), ratings_list, \
        list(Chess_df[Chess_df['Game Type'] == 'Blitz']['Played'])[::-1][0].strftime('%a, %d-%b-%Y %I:%M %p %Z')



if __name__ == "__main__":
    plot, rl, date = main()
    print (plot, '\n')
    print('Maximum Rating: {}'.format(max(rl)), end = '       ')
    print('Average Rating: {}'.format(round(np.mean(rl))), end = '       ')
    print('Current Rating: {}'.format(rl[-1]), '\n')
    print('Last Game Played On: ',date)
    
    
    
