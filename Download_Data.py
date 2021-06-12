# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 19:15:23 2021

@author: Aidan
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from selenium import webdriver

#Win lose draw function
def win_draw_lose (df):
    if df['Team A Score'] > df['Team B Score']:
        return 1
    elif df['Team A Score'] < df['Team B Score']:
        return -1
    else:
        return 0

#Return Soup with requests    
def get_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'html5lib')
    return soup

#get soup with selenium
def get_soup_sel(url):
    browser = webdriver.Chrome(r'C:\Users\Aidan\Chrome Driver\chromedriver.exe')
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html5lib')
    browser.close()
    return soup

#Get Outcome from 'https://www.soccerstats.com/results.asp?league=england&pmtype=bydate'
def get_outcomes(soup):
    for table in soup.find_all('table', attrs={'id': ['btable']}):
        pretty_table = table.prettify()
        df = pd.read_html(pretty_table)[0]
        break
    df.columns = ['Date', 'Team A', 'Score', 'Team B', 'stats', 'HT', '2.5+', 'TG', 'BTS', 'Crap']
    del df['Crap']
    df.dropna(inplace=True)
    df['Team A Score'] = df['Score'].apply(lambda x: int(x[0]))
    df['Team B Score'] = df['Score'].apply(lambda x: int(x[-1]))
    df['Outcome'] = df[['Team A Score','Team B Score']].apply(lambda x: win_draw_lose(x), axis=1)
    outcome_df = df[['Team A', 'Team B', 'Team A Score', 'Team B Score', 'Outcome']]
    return outcome_df

#Get form 'https://www.soccerstats.com/formtable.asp?league=england'
def get_form(soup):
    table = soup.find(text='Points Per Game (PPG)').find_parent('table')
    pretty_table = table.prettify()
    df = pd.read_html(pretty_table)[0]
    df.columns = ['ID','Name','Games Played', 'Points', 'PPG - Last 8', 'PPG', 'Crap1', 'Relative Form', 'Crap2']
    df.drop(['ID','Crap1','Crap2'], axis=1, inplace=True)
    return df


#get Top players from 
#urls =['https://www.thescore.com/eng_fed/news/1976310',
#       'https://www.thescore.com/eng_fed/news/1976311',
#       'https://www.thescore.com/eng_fed/news/1976312',
#      'https://www.thescore.com/eng_fed/news/1976313',
#     'https://www.thescore.com/eng_fed/news/1976314']

def get_players(soup):
    div = soup.find('div', attrs={'class': ['jsx-2885719250 content']})
    h3 = div.find_all('h3')
    h = [h.get_text() for h in h3]
    return h

def get_top_players(urls):
    h_lst = []
    for url in urls:
        soup = get_soup(url)
        h = get_players(soup)
        h_lst = h_lst + h
    
    return h_lst

def convert_lst_to_df(h_lst):
    teams = [re.search('\(([^)]+)', str(h)).group(1) for h in h_lst]
    teams_df = pd.DataFrame({'Team': teams})
    teams_count = teams_df.groupby(['Team'])['Team'].count()
    df = pd.DataFrame({'Team': teams_count.index.to_list(), 'Top_player_count': teams_count.to_list()})
    return df

def get_top_player_per_team_df(urls):
    h_lst = get_top_players(urls)
    df = convert_lst_to_df(h_lst)
    return df


#Get table from 'https://fbref.com/en/comps/9/Premier-League-Stats' 
def get_table_fbref(soup,table_id='stats_standard_squads',column_parent='Per 90 Minutes'):  
    '''
       This takes in soup from https://fbref.com/en/comps/9/Premier-League-Stats and is used to extract
       tables from that site based on table id and column parent
        Parameters
        ----------
        Soup
            * soup - Beautiful Soup of the site https://fbref.com/en/comps/9/Premier-League-Stats
        
        String
            * table_id - the table id of the table you want from the site
        
        String
            * column_parent - The level 0 column name on the table See default value for example
            
        Returns
        -------
        DataFrame
            DataFrame data from table 
    '''
    table = soup.find('table', attrs={'id': [table_id]})
    df = pd.read_html(table.prettify())[0]
    if column_parent == '':
        df_col = df.iloc[:,df.columns.get_level_values(0).str.contains('Unnamed')]
        df_col = df_col.iloc[:,~df_col.columns.get_level_values(1).str.contains('Squad')]
    else:
        df_col = df.iloc[:,df.columns.get_level_values(0)==column_parent]
        
    df_name = df.iloc[:,df.columns.get_level_values(1)=='Squad'] 
    df_out = pd.merge(df_name,df_col, left_index=True, right_index=True)
    df_out.columns = df_out.columns.get_level_values(1)
    df_out = df_out.loc[~df_out['Squad'].str.contains('vs ')]
    return df_out


def get_upcoming_games():
    url = 'https://www.soccerstats.com/results.asp?league=england'
    soup = get_soup(url)
    table = soup.find('table', attrs={'id': ['btable']})
    df = pd.read_html(table.prettify())[0]
    df.columns = ['Date', 'Team A', 'Score', 'Team B', 'stats', 'HT', '2.5+', 'TG', 'BTS', 'Crap']
    del df['Crap']
    df = df.loc[df['stats']=='h2h']
    return df