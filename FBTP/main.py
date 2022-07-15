# coding=utf-8

"""
The Team Composition based on the Football Players' Attributed Collaboration Network (TC-FPACN) model
"""

import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from FBTP import PESpre, FIFApre, fbtp, modules, greedy
import pickle
import logging


def save(filepath, params):
    with open(filepath, 'wb') as file:
        pickle.dump(params, file)
        logging.info("save parameters to %s" % filepath)


def load(filepath):
    with open(filepath, 'rb') as file:
        params = pickle.load(file).values()
        logging.info("load parameters from %s" % filepath)
        return params


def out_to_file(path, model_name):

    class logger(object):
        
        def __init__(self, file_name, path):
            self.terminal = sys.stdout
            self.log = open(os.path.join(path, file_name), mode='a', encoding='utf8')
        
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
        
        def flush(self):
            pass
    
    sys.stdout = logger(model_name + '.log', path=path)




if __name__ == '__main__':

    DATASET = 'FIFA'  # PES or FIFA

    if DATASET == 'PES':
    
        FILE_GOALKEEPER = "Goalkeeper.xlsx"
        FILE_BACK = "Back.xlsx"
        FILE_FORWARD = "Forward.xlsx"
        CRITERIA_BACK = "Criteria_Back.txt"
        CRITERIA_FORWARD = "Criteria_Forward.txt"

        ALPHA = 0.6
        BETA = 0.2
        BUDGET = 100

        FILE_PATH = BASE_DIR+'/data/'+DATASET+'/'
        cri_back = PESpre.read_criteria(FILE_PATH, CRITERIA_BACK)  # read the backward criteria
        cri_forward = PESpre.read_criteria(FILE_PATH, CRITERIA_FORWARD)  # read the forward/midfielder criteria

        # 1: the Goalkeepers
        # gks = PESpre.get_goalkeepers(FILE_PATH, FILE_GOALKEEPER)  # get all goalkeepers
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/Goalkeepers', {'gks':gks})
        gks = next(iter(load(BASE_DIR + "/FBTP/params/" + DATASET + '/Goalkeepers')))

        # 2: the Back network
        # abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
        #   PESpre.read_info(FILE_PATH, FILE_BACK)  # read backwards information
        # sim_back = modules.cal_similarity('Back', p_attrs_back)  # calculate the similarity

        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/info_back', {'abi_name_id':abi_name_id, 'p_attrs_back':p_attrs_back, 'p_abis_name_back':p_abis_name_back, 
        #                                                      'p_pos_back':p_pos_back, 'p_r_back':p_r_back, 'p_no_id_back':p_no_id_back
        #                                                      }
        #     )
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/sim_back', {'sim_back':sim_back})
        abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
            load(BASE_DIR + "/FBTP/params/" + DATASET + '/info_back')
        sim_back = next(iter(load(BASE_DIR + "/FBTP/params/" + DATASET + '/sim_back')))
        abi_avg_back = modules.cal_ability_avg(p_abis_name_back)
        # get the network of back
        pg_back = greedy.players_graph_construction(sim_back, abi_avg_back, p_abis_name_back, 
                                                    abi_name_id, p_pos_back, p_r_back
                                                    )  

        # 3: the Forward/Midfielder network
        # abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
        #   PESpre.read_info(FILE_PATH, FILE_FORWARD)  # read forward/midfielder information
        # sim_forward = modules.cal_similarity('Forward', p_attrs_forward)

        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/info_forward', {'abi_name_id':abi_name_id, 'p_attrs_forward':p_attrs_forward, 
        #                                                         'p_abis_name_forward':p_abis_name_forward, 'p_pos_forward':p_pos_forward, 
        #                                                         'p_r_forward':p_r_forward, 'p_no_id_forward':p_no_id_forward
        #                                                         }
        #     )
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/sim_forward', {'sim_forward':sim_forward})
        abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
            load(BASE_DIR + "/FBTP/params/" + DATASET + '/info_forward')
        sim_forward = next(iter(load(BASE_DIR + "/FBTP/params/" + DATASET + '/sim_forward')))
        abi_avg_forward = modules.cal_ability_avg(p_abis_name_forward)
        pg_forward = greedy.players_graph_construction(sim_forward, abi_avg_forward, p_abis_name_forward, 
                                                       abi_name_id, p_pos_forward, p_r_forward
                                                       )
    
    elif DATASET == 'FIFA':
        
        FILE_GOALKEEPER = "Goalkeeper.csv"
        FILE_BACK = "Back.csv"
        FILE_FORWARD = "Forward.csv"
        CRITERIA_BACK = "Criteria_Back.txt"
        CRITERIA_FORWARD = "Criteria_Forward.txt"

        ALPHA = 0.5
        BETA = 0.3
        BUDGET = 8

        FILE_PATH = BASE_DIR+'/data/'+DATASET+'/'
        cri_back = FIFApre.read_criteria(FILE_PATH, CRITERIA_BACK)  # read the backward criteria
        cri_forward = FIFApre.read_criteria(FILE_PATH, CRITERIA_FORWARD)  # read the forward/midfielder criteria

        # 1: the Goalkeepers
        # gks = FIFApre.get_goalkeepers(FILE_PATH, FILE_GOALKEEPER)
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/Goalkeepers', {'gks':gks})
        gks = next(iter(load(BASE_DIR + "/FBTP/params/" + DATASET + '/Goalkeepers')))
        
        # 2: the Back network
        # abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
        #     FIFApre.read_info(FILE_PATH, FILE_BACK)  # read backwards information
        # sim_back = modules.cal_similarity('Back', p_attrs_back)  # calculate the similarity
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/info_back', {'abi_name_id':abi_name_id, 'p_attrs_back':p_attrs_back, 'p_abis_name_back':p_abis_name_back, 
        #                                                      'p_pos_back':p_pos_back, 'p_r_back':p_r_back, 'p_no_id_back':p_no_id_back
        #                                                      }
        #     )
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/sim_back', {'sim_back':sim_back})
        abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
            load(BASE_DIR + "/FBTP/params/" + DATASET + '/info_back')
        sim_back = next(iter(load(BASE_DIR + "/FBTP/params/" + DATASET + '/sim_back')))
        abi_avg_back = modules.cal_ability_avg(p_abis_name_back)
        pg_back = greedy.players_graph_construction(sim_back, abi_avg_back, p_abis_name_back, 
                                                    abi_name_id, p_pos_back, p_r_back,
                                                    )  # get the network of back
        
        # 3. the Forward/Midfielder network
        # abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
        #     FIFApre.read_info(FILE_PATH, FILE_FORWARD)  # read forward/midfielder information
        # sim_forward = modules.cal_similarity('Forward', p_attrs_forward)
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/info_forward', {'abi_name_id':abi_name_id, 'p_attrs_forward':p_attrs_forward, 
        #                                                         'p_abis_name_forward':p_abis_name_forward, 'p_pos_forward':p_pos_forward, 
        #                                                         'p_r_forward':p_r_forward, 'p_no_id_forward':p_no_id_forward
        #                                                         }
        #     )
        # save(BASE_DIR+"/FBTP/params/"+DATASET+'/sim_forward', {'sim_forward':sim_forward})
        abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
            load(BASE_DIR + "/FBTP/params/" + DATASET + '/info_forward')
        sim_forward = next(iter(load(BASE_DIR + "/FBTP/params/" + DATASET + '/sim_forward')))
        abi_avg_forward = modules.cal_ability_avg(p_abis_name_forward)
        pg_forward = greedy.players_graph_construction(sim_forward, abi_avg_forward, p_abis_name_forward, 
                                                       abi_name_id, p_pos_forward, p_r_forward,
                                                       )

    fbtp.FBTP(gks, abi_name_id,
              p_no_id_back, pg_back, cri_back,
              p_no_id_forward, pg_forward, cri_forward,
              BUDGET, ALPHA, BETA, DATASET
             )
    
    # sensitivity parameters analysis (alpha and beta)
    # out_to_file(BASE_DIR + "/FBTP/results/", 'parm@' + DATASET)
    # count = 0
    # for ALPHA in [x/10 for x in range(0, 11)]:
    #     for BETA in [y/10 for y in range(0, 11-count)]:
    #         print(" ******* Begin ALPHA = %.1f, BETA = %.1f ******* " % (ALPHA, BETA))
    #         fbtp.FBTP(gks, abi_name_id,
    #                   p_no_id_back, pg_back, cri_back,
    #                   p_no_id_forward, pg_forward, cri_forward,
    #                   BUDGET, ALPHA, BETA, DATASET
    #                   )
    #         print(" ******* End.. ******* \n")
    #     count = count + 1
