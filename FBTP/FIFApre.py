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


# URLs's from CSV data in GitHub
url_goalkeepers = 'https://raw.githubusercontent.com/ShenbaoYu/TCFPACN/main/Data/FIFA/Goalkeeper.csv'
url_back = 'https://raw.githubusercontent.com/ShenbaoYu/TCFPACN/main/Data/FIFA/Back.csv'
url_forward = 'https://raw.githubusercontent.com/ShenbaoYu/TCFPACN/main/Data/FIFA/Forward.csv'

def read_criteria(path, criteria_file):
"""
- Reads a file containing player evaluation criteria
(e.g. importance of specific skills for each position).
- Normalizes the criteria values so that the total sum is 1.
"""
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


def get_goalkeepers(url_goalkeepers):
    """
    - Reads goalkeeper information from a CSV file.
    - Creates Goalkeeper objects for each goalkeeper, filling in their attributes (ID, rating, salary, skills).
    - The salary is calculated based on the goalkeeper's rating using an exponential formula.
    
    - Gets information about all goalkeepers.

    Args:
        url: URL of the CSV file containing the goalkeepers' data.

    Returns:
        A list of Goalkeeper objects.
    
    """

    goal_keepers = []
    
    # error handling if reading the CSV file fails
    try:
        _meta = pd.read_csv(url_goalkeepers, delimiter=',')  # Read the CSV once
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return goal_keepers  # Returns an empty list in case of error

    for idx, _data in _meta.iterrows(): # Use the DataFrame read in try-except
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


def read_info(url):
"""
- Reads information about players from a CSV file, differentiating between
defensive (Back) and attacking/midfield (Forward) players.
- Creates dictionaries to store:
--> Player attributes (club, nationality).
--> Player skills (with their respective values).
--> Player positions.
--> Player ratings.
--> Player IDs.
- Fills these dictionaries with the data read from the file.
- For players without a defined position, assigns a random position of the
list of possible positions for your category (Back or Forward).

    Args:
        url: URL of the CSV file containing player data.

    Returns:
        A tuple containing: ability_name_id, player_attributes, player_abilities_name,
        player_position, player_rating, player_no_id.
"""

    DIV = 'Back' if 'Back' in url else 'Forward'  # Determines DIV based on URL

    player_attributes = {}  # players attributes, including club and nationality
    player_abilities_name = OrderedDict()  # personal abilities
    player_position = {}  # players' position {id:position}
    player_rating = {}  # players' rating {id:rating}
    # player_salary = {}  # players' salary {id:salary}

    try:
        _meta = pd.read_csv(url, delimiter=',')
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return {}, {}, {}, {}, {}, {}  # Returns empty dictionaries in case of error

    attrs = [column for column in _meta][44:73]
    ability_name_id = dict(zip(attrs, [i for i in range(len(attrs))]))
    for att in attrs:
        player_abilities_name[att] = {}

    player_no_id = {}  # player's number : id
    for idx, _data in _meta.iterrows():
        player_no_id[idx] = _data['sofifa_id']  # player's id
        player_position[idx] = get_position(_data, DIV)  # player's position
        player_rating[idx] = _data['overall']  # player's rating
        
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
"""
- Helper function used by <read_info> to get a player's position.
- If the player's position in the file is valid for their category (Back or Forward), return that position.
- Otherwise, it randomly chooses a valid position from the list of positions for your category.
"""
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
"""
- Helper function used by read_criteria to normalize the values of a dictionary.
- Divides each value by the total sum of the values, ensuring that the sum of the normalized values is 1.
"""
    total = sum(v for v in dict_type.values())
    tmp = {}
    for key, value in dict_type.items():
        tmp[key] = value / total
    return tmp
