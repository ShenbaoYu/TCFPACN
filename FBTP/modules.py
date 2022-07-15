# coding=utf-8

import numpy as np




def cal_similarity(network_name, player_attributes):
    """
    :params player_attributes --> dict()
        player id : [team, nationality]
    """

    no = len(player_attributes)
    similarity = np.zeros((no, no))
    edge = 0

    for i in range(0, no-1):
        attr_i = player_attributes[i]
        for j in range(i, no-1):
            attr_j = player_attributes[j]
            sim = jaccard(attr_i, attr_j)  # calculate the similarity
            if sim > 0:
                edge += 1
            similarity[i][j] = sim
            similarity[j][i] = sim  # sim(i,j) = sim(j,i)

    density = (edge*2) / (no*no)  # the density of the players' adjacent matrix
    edge = edge - no

    print("The %s network includes %d vertex and %d edges, the density is %f" 
          % (network_name, no, edge, density)
         )

    return similarity


def jaccard(array_1, array_2):
    inter = [val for val in array_1 if val in array_2] 
    union = list(set(array_1).union(set(array_2)))
    ja = len(inter) / len(union)
    return ja


def cal_ability_avg(player_abilities_name):

    ability_avg = {}

    for ability in player_abilities_name:
        total = 0
        c = 0
        for value in player_abilities_name[ability].values():
            total = total + value
            c += 1
        ability_avg[ability] = total / c

    return ability_avg