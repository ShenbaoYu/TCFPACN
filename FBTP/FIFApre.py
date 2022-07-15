# coding=utf-8

"""
Data pre-processing for FIFA dataset
"""

import numpy as np
import pandas as pd
import random
import math
from FBTP import players
from collections import OrderedDict




def read_criteria(path, criteria_file):
    criteria = {}
    with open(path + criteria_file, 'r') as cf:
        while True:
            line = cf.readline()
            if not line:
                break
            name = line.split(":")[0]
            value = line.split(":")[1][:-1]

            criteria[name] = int(value)
    
    criteria = normalize(criteria)

    return criteria


def get_goalkeepers(path, file_name):
    """
    get all goalkeepers --> list()
    """

    goal_keepers = []

    _meta = pd.read_csv(path + file_name, delimiter=',')
    for idx, _data in _meta.iterrows():
        gk_id = _data['sofifa_id']
        gk = players.Goalkeeper(gk_id)
        gk.rating = _data['overall']  # the rating
        # gk.salary = _data['value_eur']  # salary (Euro)
        gk.salary = 0.0006375 * math.exp(0.1029*gk.rating)  # calculate salary
        gk.ability = _data.loc[['gk_diving', 'gk_handling', 'gk_kicking', 
                                'gk_reflexes', 'gk_speed', 'gk_positioning']
                              ].tolist()
        goal_keepers.append(gk)
    
    return goal_keepers


def read_info(path, file_name):

    DIV = file_name.split('.')[0]

    player_attributes = {}  # playbers attributes, including club and nationality
    player_abilities_name = OrderedDict()  # personal abilities
    player_position = {}  # players' position {id:position}
    player_rating = {}  # players' rating {id:rating}
    # player_salary = {}  # players' salary {id:salary}

    _meta = pd.read_csv(path + file_name, delimiter=',')

    attrs = [column for column in _meta][44:73]
    ability_name_id = dict(zip(attrs, [i for i in range(len(attrs))]))
    for att in attrs:
        player_abilities_name[att] = {}
    
    player_no_id = {}  # player's number : id
    for idx, _data in _meta.iterrows():
        player_no_id[idx] = _data['sofifa_id']  # player's id
        player_position[idx] = get_position(_data, DIV)  # player's position
        player_rating[idx] = _data['overall']  # player's rating
        # if _data['value_eur'] != 0:
        #     player_salary[idx] = _data['value_eur']  # salary (Euro)
        # else:
        #      player_salary[idx] = cal_player_salary(_data['overall'])
            

        # player's attributes, including club and nationality
        player_attributes[idx] = [_data['club'], _data['nationality']]
        abis = dict(_data.iloc[44:73])
        for abi, val in abis.items():
            player_abilities_name[abi][idx] = val

    return ability_name_id,       \
           player_attributes,     \
           player_abilities_name, \
           player_position,       \
           player_rating,         \
           player_no_id


def get_position(data, div):
    if div == 'Back':
        BA = ['LWB','RWB','LB','LCB','CB','RCB','RB']
        if not data['team_position'] in BA:
            return random.choice(BA)  # choose a position randomly
        else:
            return data['team_position']
    elif div == 'Forward':
        FM = ['LS','LF','CF','RF','RS','ST','LW','SS','RW',  # Forward
              'LAM','CAM','RAM','CM','LM','LCM','RCM','RM','LDM','CDM','RDM']
        if not data['team_position'] in FM:
            return random.choice(FM)  # choose a position randomly
        else:
            return data['team_position']


def normalize(dict_type):
    total = sum(v for v in dict_type.values())
    tmp = {}
    for key, value in dict_type.items():
        tmp[key] = value / total
    return tmp