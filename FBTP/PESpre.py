# coding=utf-8

"""
Data pre-processing for PES dataset
"""

import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import openpyxl
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
    get all goalkeepers
    """
    wb = openpyxl.load_workbook(path+file_name)   # open source
    ws = wb["GoalKeeper"]
    
    goal_keepers = []
    for row in range(2, ws.max_row+1):
        gk_id = ws.cell(row=row, column=1).value
        gk = players.Goalkeeper(gk_id)
        gk.rating = ws.cell(row=row, column=10).value  # the rating of goalkeeprs
        gk.salary = 0.0006375 * math.exp(0.1029*gk.rating)  # calculate salary
        
        for column in range(29, ws.max_column+1): # read skills
            gk.ability.append(ws.cell(row=row, column=column).value)
        goal_keepers.append(gk)

    return goal_keepers


def read_info(path, file_name):

    ability_name_id = {}  # ability {name:id}
    player_attributes = {}  # playbers attributes, including club and nationality
    player_abilities_name = OrderedDict()  # personal abilities
    player_position = {}  # players' position {id:position}
    player_rating = {}  # players' rating {id:rating}

    wb = openpyxl.load_workbook(path + file_name)
    ws = wb["Players"]

    player_no_id = {}  # player's number : id
    no = 0  # number of player
    ability_id = 0  # number of ability

    for row in range(1, ws.max_row + 1):
        if row == 1:
            for column in range(11, 29):  # target ability
                player_abilities_name[ws.cell(row=row, column=column).value] = {}

            for ability_name in player_abilities_name.keys():
                ability_name_id[ability_name] = ability_id
                ability_id += 1
        else:
            player_id = ws.cell(row=row, column=1).value  # get player's ID
            player_no_id[no] = player_id
            position = ws.cell(row=row, column=2).value  # get player's position
            player_position[no] = position
            rating = ws.cell(row=row, column=10).value  # get player's rating
            player_rating[no] = rating

            # player's attributes, including club and nationality
            team_name = ws.cell(row=row, column=4).value  # player's team name
            nationality = ws.cell(row=row, column=5).value  # player's nationality
            player_attributes[no] = []
            player_attributes[no].append(team_name)
            player_attributes[no].append(nationality)
            
            # player's abilities
            _ = []
            for column in range(11, 29):  # range of target abilities
                _.append(ws.cell(row=row, column=column).value)
            c = 0
            for ability in player_abilities_name:
                player_abilities_name[ability][no] = _[c]
                c += 1
            
            no += 1

    return ability_name_id,       \
           player_attributes,     \
           player_abilities_name, \
           player_position,       \
           player_rating,         \
           player_no_id


def normalize(dict_type):
    total = sum(v for v in dict_type.values())
    tmp = {}
    for key, value in dict_type.items():
        tmp[key] = value / total
    return tmp