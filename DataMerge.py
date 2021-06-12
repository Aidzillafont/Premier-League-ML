# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 19:33:19 2021

@author: Aidan
"""

import Download_Data as dd
from functools import reduce
import pandas as pd

def get_Soccer_Data():
    #outcomes
    url = 'https://www.soccerstats.com/results.asp?league=england&pmtype=bydate'
    soup = dd.get_soup(url)
    df_outcome = dd.get_outcomes(soup)
    
    #form
    url = 'https://www.soccerstats.com/formtable.asp?league=england'
    soup = dd.get_soup(url)
    df_form = dd.get_form(soup)
    
    #top_players
    urls =['https://www.thescore.com/eng_fed/news/1976310',
           'https://www.thescore.com/eng_fed/news/1976311',
           'https://www.thescore.com/eng_fed/news/1976312',
           'https://www.thescore.com/eng_fed/news/1976313',
          'https://www.thescore.com/eng_fed/news/1976314']
    df_top_players = dd.get_top_player_per_team_df(urls)
    
    #Rename some rows
    df_top_players.loc[df_top_players['Team']=='Manchester United', 'Team'] = 'Manchester Utd'
    df_top_players.loc[df_top_players['Team']=='Tottenham Hotspur', 'Team'] = 'Tottenham'
    df_top_players.loc[df_top_players['Team']=='Wolverhampton Wanderers', 'Team'] = 'Wolverhampton'
    
    
    
    #get_stats
    url = 'https://fbref.com/en/comps/9/Premier-League-Stats'
    soup = dd.get_soup_sel(url)
    
    df_standard = dd.get_table_fbref(soup, table_id='stats_standard_squads',column_parent='Per 90 Minutes')
    df_keeper = dd.get_table_fbref(soup,table_id='stats_keeper_squads',column_parent='Performance')
    df_shoot_stats = dd.get_table_fbref(soup,table_id='stats_shooting_squads',column_parent='Standard')
    df_shoot_stats_ex = dd.get_table_fbref(soup,table_id='stats_shooting_squads',column_parent='Expected')
    df_shot_creation = dd.get_table_fbref(soup,table_id='stats_gca_squads',column_parent='SCA')
    df_goal_creation = dd.get_table_fbref(soup,table_id='stats_gca_squads',column_parent='GCA')
    df_poss = dd.get_table_fbref(soup,table_id='stats_possession_squads',column_parent='')
    
    data_frames = [df_standard,df_keeper,df_shoot_stats,
                   df_shoot_stats_ex,df_shot_creation,
                   df_goal_creation,df_poss]
    
    df_fbref = reduce(lambda left,right: pd.merge(left,right,on=['Squad'],how='outer'), data_frames)
    
    
    #Rename some rows
    df_fbref.loc[df_fbref['Squad']=='West Ham', 'Squad'] = 'West Ham Utd'
    df_fbref.loc[df_fbref['Squad']=='Wolves', 'Squad'] = 'Wolverhampton'
    df_fbref.loc[df_fbref['Squad']=='Leeds United', 'Squad'] = 'Leeds Utd'
    
    
    #Now Merge
    df_full_stats = pd.merge(df_form, df_fbref, left_on='Name',right_on='Squad')
    df_full_stats = pd.merge(df_full_stats, df_top_players, left_on='Name',right_on='Team', how='left')
    
    #Clean some columns
    df_full_stats.drop(['Squad','Team'], axis=1, inplace=True)
    df_full_stats['Top_player_count'] = df_full_stats['Top_player_count'].fillna(0)
    
    #Create home and away table
    df_fs_a = df_full_stats.add_suffix('_A')
    df_fs_b = df_full_stats.add_suffix('_B')
    
    #Merge with outcome table
    dfa = pd.merge(df_outcome, df_fs_a, left_on='Team A', right_on='Name_A')
    df_all = pd.merge(dfa, df_fs_b, left_on='Team B', right_on='Name_B')
    
    df_all.to_csv('Soccer_Data.csv')