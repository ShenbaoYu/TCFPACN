# coding=utf-8

"""
Discovering a cohesive team based on FBTP algorithm
"""

import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from FBTP import greedy
from FBTP import players as ps




def FBTP(gks, abi_name_id,
         p_no_id_back, pg_back, cri_back,
         p_no_id_forward, pg_forward, cri_forward,
         budget, alpha, beta, datasource):
    """
    FUNCTION: team composition based on Finding Best Team with Pruning (FBTP) model
    (1) we first discover the team without budget constraint;
    (2) we prune the team if the cost exceeds the budget
    """

    print("The Budget Constraint is:%.3f" % budget)

    team = {}

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # +                                                                 +
    # +         Select the players without budget constraint            +
    # +                                                                 +
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    print('Select the players without budget constraint ')
    # find the best goalkeeper
    team["GK"] = list()
    best_gk = best_goalkeeper(gks)
    team["GK"].append(best_gk.get_id())

    # select the best backwards
    team["Back"] = list()
    opt_back = greedy.player_opt_subgraph(p_no_id_back, pg_back, cri_back, 
                                          abi_name_id, alpha, beta, 'Back',
                                          datasource
                                          )
    team["Back"] = opt_back

    # select the forward/midfielder
    team["Forward"] = list()
    opt_forward = greedy.player_opt_subgraph(p_no_id_forward, pg_forward, cri_forward, 
                                             abi_name_id, alpha, beta, 'Forward',
                                             datasource
                                            )
    team["Forward"] = opt_forward

    # 1. calculate the total cost
    # 2. calculate the  average team ability
    # 3. calculate the heterogeneity
    team_cost, team_ability, homo_back, homo_forward, opt_player_cf \
        = cal_cost_abi_homo(team, gks, pg_back, pg_forward, cri_back, 
                            cri_forward, abi_name_id
                           )


    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # +                                                                 +
    # +         Pruning if necessary                                    +
    # +                                                                 +
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    team_real = {"GK": [], "Back": [], "Forward": []}

    while True:

        if team_cost < budget:
            team_real["GK"].append(team["GK"][0])  # goalkeeper ID
    
            for i in team["Back"]:
                team_real["Back"].append(p_no_id_back[i])
    
            for j in team["Forward"]:
                team_real["Forward"].append(p_no_id_forward[j])
            print("\n",
                  "\t", "The optimal players are:", team_real, "\n",
                  "\t", "The total cost is:", round(team_cost, 3), "\n",
                  "\t", "The average team ability is:", round(team_ability, 3), "\n",
                  "\t", "The cost performance is:", opt_player_cf, "\n",
                  "\t", "The homogeneity of backward is: %.4f" % homo_back, "\n",
                  "\t", "The heterogeneity of forward/midfielder is: %.4f" % homo_forward,
                  "\n")

            break
        else:
            # Pruning
            team_update = cut_base_cf(opt_player_cf, team, pg_back, pg_forward, gks,
                                      cri_back, cri_forward, abi_name_id,
                                      alpha=0.7, beta=0.15)
            # calculate cost, average ability and homogeneity
            team_up_cost, team_up_ability, homo_up_back, homo_up_forward, opt_player_cf_up\
                = cal_cost_abi_homo(team, gks, pg_back, pg_forward, cri_back, cri_forward, abi_name_id)

            # update
            team = team_update
            team_cost = team_up_cost
            team_ability = team_up_ability
            homo_back = homo_up_back
            homo_forward = homo_up_forward
            opt_player_cf = opt_player_cf_up

            print('Pruning... the current team cost is %.2f' % team_cost)

    return team_real


def best_goalkeeper(gks):
    opt_gk = ''
    score_max = 0
    for gk in gks:
        # calculate the personal aboility of goalkeeper
        gk_score = sum(gk.ability) / len(gk.ability)
        if score_max < gk_score:
            score_max = gk_score
            opt_gk = gk
    print("The best goalkeeper without budget constraint is:", opt_gk.id)

    return opt_gk


def cal_cost_abi_homo(team, gks, pg_back, pg_forward, cri_back, cri_for, abi_name_id):

    team_cost = 0
    team_ability = 0
    homo_back = 0
    homo_forward = 0
    opt_player_cf = {}  # cost performance = ability / salary

    for pos in team.keys():
        if pos == "GK":
            gk = [gk for gk in gks if gk.id == team[pos][0]][0]
            cost = gk.get_salary()
            team_cost += cost
            abi = sum(gk.ability)/len(gk.ability)
            team_ability += abi

            opt_player_cf[gk.id] = round(abi/cost, 3)

        elif pos == "Back":
            homo_back = cal_homo(team[pos], pg_back)
            for i in team[pos]:
                cost = pg_back.vertexList[i].salary
                team_cost += cost
                abi = greedy.cal_player_ability(pg_back.vertexList[i].abilities, cri_back, abi_name_id)
                team_ability += abi
                opt_player_cf[i] = round(abi/cost, 3)

        elif pos == "Forward":
            homo_forward = cal_homo(team[pos], pg_forward)
            for j in team[pos]:
                cost = pg_forward.vertexList[j].salary
                team_cost += cost
                abi = greedy.cal_player_ability(pg_forward.vertexList[j].abilities, cri_for, abi_name_id)
                team_ability += abi
                opt_player_cf[j] = round(abi/cost, 3)

    team_ability = team_ability / 11

    return team_cost, team_ability, homo_back, homo_forward, opt_player_cf


def cut_base_cf(player_cf, team, pg_back, pg_forward, gks, cri_back, cri_for, abi_name_id, alpha, beta):
    """
    FUNCTION: Pruning based on the cost performance
    """

    # 1. find the player with the lowest of cost performance
    cut_player = ps.CutPlayer(None)
    cf_min = sys.maxsize
    for p, cf in player_cf.items():
        if cf < cf_min:
            cf_min = cf
            cut_player.id = p

    # 2. delete the player
    for pos, players in team.items():
        if cut_player.id in players:
            players.remove(cut_player.id)
            cut_player.cut_pos = pos
            break

    # 3. find candidate player
    candidate = None

    if cut_player.get_cut_pos() == "Back":

        cut_player.cut_salary = pg_back.vertexList[cut_player.get_id()].salary
        cut_player.cut_position = pg_back.vertexList[cut_player.get_id()].position
        candidate = select_candidate(team[cut_player.get_cut_pos()], pg_back, cut_player,
                                     cri_back, abi_name_id, alpha, beta)
        team[cut_player.get_cut_pos()].append(candidate)

    elif cut_player.get_cut_pos() == "Forward":

        cut_player.cut_salary = pg_forward.vertexList[cut_player.get_id()].salary
        cut_player.cut_position = pg_forward.vertexList[cut_player.get_id()].position
        candidate = select_candidate(team[cut_player.get_cut_pos()], pg_forward, cut_player,
                                     cri_for, abi_name_id, alpha, beta)
        team[cut_player.get_cut_pos()].append(candidate)

    else:
        # the player to be cut is goalkeeper
        opt_abi = 0
        for gk in gks:
            if gk.id == cut_player.get_id():
                cut_player.cut_salary = gk.get_salary()
                continue
            abi = sum(gk.ability)/len(gk.ability)
            if opt_abi < abi and gk.get_salary() < cut_player.get_cut_salary():
                opt_abi = abi
                candidate = gk.id
        team["GK"].append(candidate)

    return team


def select_candidate(team_sub, pg, cut_player, criteria, abi_name_id, alpha, beta):

    neighbor = list()
    for player in team_sub:
        for key in pg.vertexList[player].connectedTo.keys():
            # focus only on the position to be cut and neglect the players has been selected
            if key.id not in neighbor and\
                    key.id not in team_sub and key.id != cut_player.get_id() and\
                    key.position == cut_player.get_cut_position():
                neighbor.append(key.id)

    # function = ability + density + homogeneity
    density = {}
    team_ability = {}
    team_gini = {}
    team_homo = {}
    for ne in neighbor:
       
        ne_abi = greedy.cal_player_ability(
            pg.vertexList[ne].abilities, criteria, abi_name_id)
        
        weight = 0
        te_abi = ne_abi
        for op in team_sub:
            if pg.vertexList[op] in pg.vertexList[ne].connectedTo:
                weight += pg.vertexList[ne].get_weight(pg.vertexList[op])
                te_abi += greedy.cal_player_ability(pg.vertexList[op].abilities, criteria, abi_name_id)

        gini = greedy.cal_homogeneity(pg.vertexList, ne, team_sub)

        d = weight / (len(team_sub) + 1)
        density[ne] = d
        team_ability[ne] = te_abi
        team_gini[ne] = gini

    if cut_player.get_cut_pos() == "Back":
        for key, value in team_gini.items():
            team_homo[key] = 1 / value
    elif cut_player.get_cut_pos() == "Forward":
        for key, value in team_gini.items():
            team_homo[key] = value

    # find the best player with team ability + density + homogeneity
    score_final = {}
    score_max = 0
    candidate = None

    team_ability_nor = greedy.normalize_min_max(team_ability)
    team_homo_nor = greedy.normalize_min_max(team_homo)

    for player_id, value in team_ability_nor.items():
        # score = abilities + density + homogeneity
        score = alpha * team_ability_nor[player_id] +\
                beta * density[player_id] +\
                (1 - alpha - beta) * (team_homo_nor[player_id])

        score_final[player_id] = score

        if score_max < score and \
           pg.vertexList[player_id].salary < cut_player.get_cut_salary():
            score_max = score
            candidate = player_id

    return candidate


def cal_homo(team, pg):
    homo = 0
    diff = {}
    avg_tmp = {}
    avg = {}
    gini_co = {}

    for i in range(0, len(team)):
        for j in range(0, len(team)):
            for abi_id in pg.vertexList[i].abilities.keys():
                d = abs(pg.vertexList[team[i]].abilities[abi_id] -
                        pg.vertexList[team[j]].abilities[abi_id])
                if abi_id not in diff:
                    diff[abi_id] = d
                else:
                    diff[abi_id] += d

    for player in team:
        for abi_id in pg.vertexList[player].abilities.keys():
            if abi_id not in avg_tmp:
                avg_tmp[abi_id] = pg.vertexList[player].abilities[abi_id]
            else:
                avg_tmp[abi_id] += pg.vertexList[player].abilities[abi_id]

    for abi_id, value in avg_tmp.items():
        avg[abi_id] = avg_tmp[abi_id]/len(team)

    for abi_id in diff.keys():
        gini_co[abi_id] = (1 / (2 * pow(len(team), 2) * avg[abi_id])) * diff[abi_id]

    for value in gini_co.values():
        homo += value

    homo = homo / len(gini_co)

    return homo
