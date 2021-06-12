# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 19:56:15 2021

@author: Aidan
"""

import DataMerge as d
import pandas as pd
from Download_Data import get_upcoming_games
import os
import datetime as dt

def create_prediction_df(model, upcoming_games_df, features_A, features_B):
    df = pd.read_csv('Soccer_Data.csv', index_col='Unnamed: 0')
    predictions_list = []
    
    for date, home, away in zip(upcoming_games_df['Date'],
                              upcoming_games_df['Team A'],
                              upcoming_games_df['Team B']):
        A_name = df.loc[df['Team A']==home]['Team A'].iloc[0]
        B_name = df.loc[df['Team B']==away]['Team B'].iloc[0]
        A_data = list(df.loc[df['Team A']==home][features_A].iloc[0])
        B_data = list(df.loc[df['Team B']==away][features_B].iloc[0])
        new_data = [A_data+B_data]
        prediction = model.predict(new_data)
        prediction_prob = model.predict_proba(new_data)
        
        if prediction[0] == 1:
            outcome = 'Home Win'
        elif  prediction[0] == -1:
            outcome = 'Away Win'
        else:
            outcome = 'Draw'
        
        predic_list = [date,A_name,B_name,outcome,
                       prediction_prob[0][2], 
                       prediction_prob[0][0], 
                       prediction_prob[0][1]]
        
        predictions_list.append(predic_list)
    
    df_predictions = pd.DataFrame(predictions_list, columns=['Date','Home Team','Away Team','Outcome',
                                           'H/W Prob','A/W Prob', 'Draw Prob'])
    return(df_predictions)

def created_soccer_file_today(file):
    creation_date_float = os.path.getctime(file)
    creation_date = dt.datetime.fromtimestamp(creation_date_float)
    if creation_date.date() == dt.datetime.now().date():
        return True
    else:
        return False


if not created_soccer_file_today('Soccer_Data.csv'):
    d.get_Soccer_Data()


df = pd.read_csv('Soccer_Data.csv', index_col='Unnamed: 0')
corr_matrix = df.corr()

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
#from sklearn.preprocessing import StandardScaler

features_A = ['PPG_A','Top_player_count_A','SoT/90_A','GCA90_A','xG_x_A','Poss_A']
features_B = ['PPG_B','Top_player_count_B','SoT/90_B','GCA90_B','xG_x_B','Poss_B']
features = features_A + features_B
labels = df['Outcome']

num_pipline = Pipeline([
    ('impute',SimpleImputer(strategy='median')),
])

train_prepared = num_pipline.fit_transform(df[features])


from sklearn.ensemble import ExtraTreesClassifier
ext_reg = ExtraTreesClassifier(n_estimators=100)


from sklearn.model_selection import GridSearchCV

n_estimators = [100,200,300]
depth = [2,5,10,20,30]
min_samples_leaf = [1, 2, 4]
bootstrap = [True, False]

param_grid = {'n_estimators': n_estimators,
             'max_depth':depth,
             'min_samples_leaf': min_samples_leaf,
              'bootstrap':bootstrap,
             }
#n_jobs=-1 means it will use all your cores
grid = GridSearchCV(ext_reg, param_grid=param_grid, cv=10, scoring='accuracy',n_jobs=-1)

grid.fit(train_prepared,labels)

print('Best Score:', grid.best_score_)
print('Best Estimator:', grid.best_estimator_)

upcoming_games_df = get_upcoming_games()

df_pred = create_prediction_df(grid, upcoming_games_df, features_A, features_B)
df_pred.to_csv('Predictions.csv')
