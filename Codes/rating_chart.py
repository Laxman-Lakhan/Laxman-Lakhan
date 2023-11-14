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
    main_dict = {'Played':[], 'My Rating':[], 'Rating Fluctuation':[], 'Opponent Rating': [], 'Winner': [], 'My Color': []}
    data_length = len(data)
    for i in range(data_length):
        if data[i]['players']['white']['user']['id'] == 'yourkingisindanger':
            main_dict['My Rating'].insert(0,data[i]['players']['white']['rating'])
            main_dict['Opponent Rating'].insert(0,data[i]['players']['black']['rating'])
            main_dict['My Color'].insert(0,'White')
            try:
                main_dict['Rating Fluctuation'].insert(0,data[i]['players']['white']['ratingDiff'])
            except:
                main_dict['Rating Fluctuation'].insert(0,0)
        else:
            main_dict['My Rating'].insert(0,data[i]['players']['black']['rating'])
            main_dict['Opponent Rating'].insert(0,data[i]['players']['white']['rating'])
            main_dict['My Color'].insert(0,'Black')
            try:
                main_dict['Rating Fluctuation'].insert(0,data[i]['players']['black']['ratingDiff'])
            except:
                main_dict['Rating Fluctuation'].insert(0,0)
        main_dict['Played'].insert(0,data[i]['lastMoveAt'].astimezone(pytz.timezone('Asia/Kolkata')))
        
        try:
            main_dict['Winner'].insert(0,data[i]['winner'].capitalize())
        except:
            main_dict['Winner'].insert(0,None)
    return main_dict


def data_formation(main_dict):
    url = 'https://github.com/Laxman-Lakhan/Laxman-Lakhan/blob/d72c599f65d5d4d91742b5ba0842e758094ec852/Codes/dP.csv?raw=true'
    dP = pd.read_csv(url)
    dP.drop(['Unnamed: 0'], axis = 1, inplace = True)
    Chess_df = pd.DataFrame.from_dict(main_dict, orient ='columns')
    Chess_df.reset_index(inplace = True)
    Chess_df['New Rating'] = Chess_df['My Rating'] + Chess_df['Rating Fluctuation']
    Chess_df.loc[Chess_df['Winner'] == Chess_df['My Color'], 'Result'] = 1
    Chess_df.loc[(Chess_df['Winner'] != Chess_df['My Color']) & (Chess_df['Winner'] != None), 'Result'] = 0
    Chess_df.loc[Chess_df['Winner'].isna(), 'Result'] = 0.5
    Chess_df.drop(['Winner', 'My Color'], axis = 1, inplace = True)
    
    k = 100
    Chess_df['Ra'] = Chess_df['Opponent Rating'].rolling(k).mean()
    Chess_df['p'] = round(Chess_df['Result'].rolling(k).sum()/k, 2)
    Chess_df = Chess_df.merge(dP, on='p')
    Chess_df['Performance'] = round(Chess_df['Ra'] + Chess_df['dp'], 0)
    Chess_df.sort_values('index', inplace = True)
    Chess_df.reset_index(inplace = True)
    Chess_df.drop(columns = ['level_0', 'index', 'Ra', 'dp', 'p', 'Result', 'My Rating', 
                       'Rating Fluctuation', 'Opponent Rating'], inplace = True)
    return Chess_df
    
    
def main():
    Chess_df = data_formation(dict_formation(data_extractor()))
    ratings_list = list(Chess_df['New Rating'])[::-1][0:100][::-1]
    performance_list = list(Chess_df['Performance'])[::-1][0:100][::-1]
    return (ac.plot(ratings_list, {'height': 15, 'format':'{:4.0f}'})), ratings_list, performance_list, list(Chess_df['Played'])[::-1][0].strftime('%a, %d-%b-%Y %I:%M %p %Z')


if __name__ == "__main__":
    plot, rl, pl, date = main()
    print (plot, '\n')
    print('Current Rating: {}'.format(rl[-1]), '\n')
    print('Highest Rating: {}'.format(max(rl)))
    print('Performance   : {}'.format(pl[-1]))
    print('Average Rating: {}'.format(round(np.mean(rl))))
    print('Last Game Played On:',date)
    
