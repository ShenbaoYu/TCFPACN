# coding=utf-8

"""
build the team (Forward/Midfielder + Backwards) 
based on greedy algorithm in the context of players' social network

A node in the graph denotes a football players with the personal ability
edge denotes the similarity between two players based on the club and nationality
"""

import os, sys

from regex import I
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from FBTP import players, modules
import re
import math
import numpy as np




def players_graph_construction(sim, abi_avg, abis_name, abi_name_id, pos, rating):
    """
    FUNCTION: Players' Graph
    """

    # abilities_name = modules.player_abilities_name
    # ability_name_id = modules.ability_name_id
    # player_position = modules.player_position
    # player_rating = modules.player_rating

    # get the major abilities
    ability_major = []
    c = 1
    tmp_sorted = sorted(abi_avg.items(), key=lambda x: x[1], reverse=True)
    for abl in tmp_sorted:
        if c <= 10:
            ability_major.append(abl[0])
            c += 1
    players_graph = players.Graph()

    # construct the players' network based on similarity
    # O(|node|^2)
    for i in range(0, sim.shape[0]-1):

        if not players_graph.__contains__(i):
            players_graph.add_vertex(i)

        # add the player's abilities
        for name, abilities in abis_name.items():
            if name in ability_major and i in abilities:
                players_graph.vertexList[i].abilities[abi_name_id[name]] = abilities[i]

        # find the neighbors
        neighbors = np.argwhere(sim[i] != 0).tolist()
        neighbors.remove([i])
        for ne in neighbors:
            players_graph.add_edge(i, ne[0], sim[i][ne[0]])
        # for j in range(0, sim.shape[0]-1):
        #     if i != j and sim[i][j] > 0:
        #         players_graph.add_edge(i, j, sim[i][j])

        # add the position
        players_graph.vertexList[i].position = pos[i]

        # calculate the salary
        players_graph.vertexList[i].salary = cal_player_salary(i, rating)

    return players_graph


def cal_player_salary(i, player_rating):
    eta = 0.0006375
    theta = 0.1029
    salary = eta * math.exp(theta*player_rating[i])
    return salary


def player_opt_subgraph(player_no_id, pg, criteria, abi_name_id, alpha, beta, network_name, datasource):
    """
    FUNCTION: find the optimal subgraph based on greedy algorithm
    STEP 1:
        find a centre player maximize balance= alpha*φ(i)+(1-alpha)*s(i)
    STEP 2:
        find other football players
    STEP 3:
        repeat STEP 2 until find K players

    """

    # pick a centre player
    star = select_star(player_no_id, pg.vertexList, criteria, abi_name_id, alpha=0.8)
    # find the best player set
    opt_players = select_opt_players(player_no_id, pg.vertexList, criteria, abi_name_id,
                                     alpha, beta, star, network_name, datasource
                                    )

    return opt_players


def select_star(player_num_id, vertex_list, criteria, abi_name_id, alpha):
    star = None
    star_score = 0

    player_pa_de = {}  # player ID:[ability value, degree]

    # normalize based on min-max
    pa_min = sys.maxsize
    pa_max = 0
    de_min = sys.maxsize
    de_max = 0

    for player_id, vertex in vertex_list.items():
        player_pa_de[player_id] = []

        # calculate the football players' ability - player ability(pa)
        pa = cal_player_ability(vertex.abilities, criteria, abi_name_id)
        player_pa_de[player_id].append(pa)
        if pa > pa_max:
            pa_max = pa
        if pa < pa_min:
            pa_min = pa

        # calculate the degree - degree(de)
        de = cal_player_degree(vertex.connectedTo)
        player_pa_de[player_id].append(de)
        if de > de_max:
            de_max = de
        if de < de_min:
            de_min = de

    for key, value in player_pa_de.items():
       
        player_id = key
        score = alpha*(value[0]-pa_min)/(pa_max-pa_min) + (1-alpha)*(value[1]-de_min)/(de_max-de_min)

        if star_score < score:
            star = player_id
            star_score = score

    player_real_id = player_num_id[star]
    print("alpha = %.1f, the centre player is: %s" % (alpha, player_real_id))

    return star

def cal_player_ability(abilities, criteria, abi_name_id):
    player_ability = 0

    for abi_id, score in abilities.items():
        abi_name = list(abi_name_id.keys())[list(abi_name_id.values()).index(abi_id)]
        player_ability += criteria[abi_name] * score

    return player_ability


def cal_player_degree(player_co):
    degree = len(player_co)
    return degree


def select_opt_players(player_num_id, vertex_list, criteria, ability_name_id, alpha, beta, star, network_name, datasource, k=1):
    """
    FUNCTION: Find the players
    """
    # the number of players in each position
    if datasource == 'PES':
        position_num = {"CB": 2, "LB": 1, "RB": 1, "CF/SS": 1, "LWF": 1, "RWF": 1, "*MF": 3}
    elif datasource == 'FIFA':
        position_num = {"CB": 2, "LB": 1, "RB": 1, "MID": 3, "FOR": 3}
        

    opt_players = list()  # initialize the optimal player set
    opt_players_position = {}  # initialize the position

    opt_players.append(star)  # add the centre player
    opt_players_position[player_num_id[star]] = vertex_list[star].position
    update_position(position_num, vertex_list[star].position, datasource)

    threshold = 4  # the maximum number of players to be selected
    if network_name == "Forward":
        threshold = 6

    while k < threshold:
        # get all neighbors of opt_players
        neighbor = list()
        for player in opt_players:
            for key in vertex_list[player].connectedTo.keys():
                if key.id not in neighbor and key.id not in opt_players and \
                   position_num[position_trans(key.position, datasource)] != 0:
                    neighbor.append(key.id)

        # function = ability + density + homogeneity
        density = {}
        team_ability = {}
        team_gini = {}
        team_homo = {}
        for ne in neighbor:  # walk through all neighbors
            # calculate the personal ability of neighbor
            ne_abi = cal_player_ability(vertex_list[ne].abilities, criteria, ability_name_id)
            # calculate the weights and abilities of neighbor with opt_players
            weight = 0
            te_abi = ne_abi
            for op in opt_players:
                if vertex_list[op] in vertex_list[ne].connectedTo:
                    # cumulate the weight
                    weight += vertex_list[ne].get_weight(vertex_list[op]) 
                    # cumulate the team ability
                    te_abi += cal_player_ability(vertex_list[op].abilities, criteria, ability_name_id)

            # calculate the Gini coefficient
            gini = cal_homogeneity(vertex_list, ne, opt_players)

            d = weight / (len(opt_players)+1)  # calculate the density
            density[ne] = d
            team_ability[ne] = te_abi
            team_gini[ne] = gini

        if network_name == "Back":
            for key, value in team_gini.items():
                team_homo[key] = 1/value  # homogeneity
        elif network_name == "Forward":
            for key, value in team_gini.items():
                team_homo[key] = value  # heterogeneity

        # find the best player with maximum team ability + density + homogeneity
        score_max = 0
        candidate = None
        team_ability_nor = normalize_min_max(team_ability)  # normalize the team ability
        # density_nor = normalize_min_max(density)
        team_homo_nor = normalize_min_max(team_homo)  # normalize the heterogeneity

        for player_id, value in team_ability_nor.items():
            # score = abilities + density + homogeneity
            score = alpha * team_ability_nor[player_id] + \
                    beta * density[player_id] + \
                    (1-alpha-beta) * (team_homo_nor[player_id])

            if score_max < score:
                score_max = score
                candidate = player_id

        # add the best player
        opt_players.append(candidate)
        update_position(position_num, vertex_list[candidate].position, datasource)
        opt_players_position[player_num_id[candidate]] = vertex_list[candidate].position

        k += 1

    # get the player ID
    opt_players_real = []
    for player_id in opt_players:
        opt_players_real.append(player_num_id[player_id])

    print("The best players are:", opt_players_real)
    print("The positions of each players are:", opt_players_position)

    return opt_players


def update_position(position_num, player_position, datasource):
    """ Update the number of players in position"""
    position = position_trans(player_position, datasource)
    position_num[position] -= 1

    return position_num


def position_trans(player_position, datasource):
    if datasource == 'PES':
        if re.match(r".+MF", player_position):
            player_position = "*MF"
        elif player_position == "CF" or player_position == "SS":
            player_position = "CF/SS"
    elif datasource == 'FIFA':
        FOR = ['LS','LF','CF','RF','RS','ST','LW','SS','RW']  # Forward
        MID = ['LAM','CAM','RAM','CM','LM','LCM','RCM','RM','LDM','CDM','RDM']  # Midfielder
        RBS = ['RWB','RCB','RB']  # RB
        LBS = ['LWB','LCB','LB']  # LB
        if player_position in FOR:
            player_position = 'FOR'
        elif player_position in MID:
            player_position = 'MID'
        elif player_position in RBS:
            player_position = 'RB'
        elif player_position in LBS:
            player_position = 'LB'

    return player_position


def cal_homogeneity(vertex_list, neighbor, opt_players):

    homo = 0
    com_players = list()

    com_players.append(neighbor)
    for p in opt_players:
        com_players.append(p)

    diff = {}
    avg_tmp = {}
    avg = {}
    gini_co = {}

    # calculate the difference of ability between players
    for i in range(0, len(com_players)):
        for j in range(0, len(com_players)):
            for abi_id in vertex_list[i].abilities.keys():
                d = abs(vertex_list[com_players[i]].abilities[abi_id] -
                        vertex_list[com_players[j]].abilities[abi_id])
                if abi_id not in diff:
                    diff[abi_id] = d
                else:
                    diff[abi_id] += d

    # calculate the average of ability
    for player in com_players:
        for abi_id in vertex_list[player].abilities.keys():
            if abi_id not in avg_tmp:
                avg_tmp[abi_id] = vertex_list[player].abilities[abi_id]
            else:
                avg_tmp[abi_id] += vertex_list[player].abilities[abi_id]

    for abi_id, value in avg_tmp.items():
        avg[abi_id] = avg_tmp[abi_id]/len(com_players)

    # calculate the Gini coefficient of each ability
    for abi_id in diff.keys():
        gini_co[abi_id] = (1/(2*pow(len(com_players), 2)*avg[abi_id])) * diff[abi_id]

    # calculate the average of Gini coefficient
    for value in gini_co.values():
        homo += value

    homo = homo / len(gini_co)

    return homo


def normalize(dict_type):
    total = sum(v for v in dict_type.values())
    tmp = {}
    for key, value in dict_type.items():
        tmp[key] = value / total
    return tmp


def normalize_min_max(dict_type):

    value_min = sys.maxsize
    value_max = 0

    for value in dict_type.values():
        if value > value_max:
            value_max = value
        if value < value_min:
            value_min = value

    tmp = {}
    for key, value in dict_type.items():
        tmp[key] = (value-value_min)/(value_max-value_min)

    return tmp