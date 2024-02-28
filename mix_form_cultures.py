'''

'''
import numpy as np
from random import randrange, choice
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import ListedColormap
import copy
import json
import time
from functools import partial
from itertools import permutations
from py_logs import get_logger
logger = get_logger(__name__)
from multiprocess import Pool
if __name__ == '__main__':
    ## Parameters

    Ni = 5
    Nj = 5

    Ncul = 5

    iz = range(Ni)
    jz = range(Nj)

    coords0 = [[i, j] for i in iz for j in jz]

    path_tetris = '/home/chilly-ben/Documents/Créations/Code/tiwanaku/tetris_forms.json'
    with open(path_tetris, "r") as fp:
        tetris_forms = json.load(fp)

    start = time.time()

    ##

    permuts = []
    for size in range(1, Ncul+1):
        permuts.append([[ind for ind in permut] for permut in permutations(range(1,size+1))])
        # permuts.append(list(permutations(range(1,size+1))))

    ## Functions


    def fun_big_neighbors(ter):
        i, j = ter
        return [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]]


    def fun_forms_in_remaining(ter, remaining_ters, size_reg):
        i,j = ter
        all_forms = [[[a+i,b+j] for a,b in reg] for reg in tetris_forms[size_reg-1][:]]
        possible_forms = []
        for reg in all_forms:
            if all(item in remaining_ters for item in reg):
                reg.sort()
                if reg not in possible_forms:
                    possible_forms.append(reg)

                    # possible_forms = list(reg for reg,_ in itertools.groupby(possible_forms_tmp))
                    # set(reg) <= set(remaining_ters)]
        return possible_forms


    def rec_form(remaining_ters0, list_forms0, list_boards0, impossibilities0, cultures_sol0, region_cults):
        region, cults = region_cults
        list_forms = copy.deepcopy(list_forms0)
        list_boards = copy.deepcopy(list_boards0)
        impossibilities = copy.deepcopy(impossibilities0)
        cultures_sol = copy.deepcopy(cultures_sol0)

        if region:
            list_forms.append(region)
            for ter, cult in zip(region, cults):
                i,j = ter
                cultures_sol[i][j] = cult
                neighbors = fun_big_neighbors(ter)
                impos_tmp = [ter for ter in neighbors if ter in coords0]
                for a,b in impos_tmp:
                    if cult not in impossibilities[a][b]:
                        impossibilities[a][b].append(cult)
        remaining_ters = [ter for ter in remaining_ters0 if ter not in region]
        if not remaining_ters:
            list_boards.append([list_forms, cultures_sol])
        else:
            ter = remaining_ters[0]
            for size_reg in range(1,Ncul+1):
                possible_forms = fun_forms_in_remaining(ter, remaining_ters, size_reg)
                for region in possible_forms:
                    # if not list_forms:
                    #     print(region, time.time()-start)
                    if len(list_forms) == 1:
                        print(list_forms[0], region, time.time()-start, sep = '     ')
                    for cults in permuts[size_reg-1]:
                        for ind_cult, cult in enumerate(cults):
                            i,j = region[ind_cult]
                            if cult in impossibilities[i][j]:
                                break
                        else:
                            list_boards = rec_form(remaining_ters, list_forms, list_boards, impossibilities, cultures_sol, [region, cults])
        return list_boards

    impossibilities0 = [[[] for j in jz] for i in iz]
    cultures_sol0 = [[0 for j in jz] for i in iz]
    region = []
    cults = []
    remaining_ters0 = coords0.copy()
    list_forms0 = []
    list_boards0 = []

    # lis = rec_form(remaining_ters0, list_forms0, list_boards0, impossibilities0, cultures_sol0, [region, cults])

    ##

    first_couples = []
    for size_reg in range(1,Ncul+1):
        forms_size = fun_forms_in_remaining([0,0], remaining_ters0, size_reg)
        for region in forms_size:
            for cults in permuts[size_reg-1]:
                first_couples.append([region, cults])

    lis = []

    # # for couple in first_couples:
    # #     lis.extend(rec_form(remaining_ters0, list_forms0, list_boards0, impossibilities0, couple))


    p = Pool(12)
    results = p.map(partial(rec_form, remaining_ters0, list_forms0, list_boards0, impossibilities0, cultures_sol0), first_couples)
    p.close()
    p.join()
    for res in results:
        lis.extend(res)

##

    print(len(lis))
    # for ter,cult in lis:
    #     print(ter)
    #     print(cult)
    #     print()

    ##

    if 1:
        with open('/home/chilly-ben/Documents/Créations/Code/tiwanaku/solution_forms.json', "w") as fp:
            json.dump(lis, fp)

    ##

    # ##########

    # plt.close('all')

    # list_unsorted0 = list_sorted0.copy()
    # list_unsorted0.reverse()

    # board = np.full((Ni, Nj), 0)
    # for ind, region in enumerate(list_unsorted0):
    #     for i,j in region:
    #         board[i,j] = ind
    #
    # colors = ['brown', 'yellow', 'green', 'blue']
    # minor_y = np.arange(0.5, Ni-1)
    # minor_x = np.arange(0.5, Nj-1)
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(1, 1, 1)
    #
    # cmap = ListedColormap(colors)
    # # ax.imshow(board_cols, cmap = cmap)
    # # ax.imshow(board, cmap = cmap)
    # ax.imshow(board, cmap = 'tab20c')
    #
    #
    # # ax.set_yticks(jz, jz[::-1])
    # ax.set_xticks(minor_x, minor=True)
    # ax.set_yticks(minor_y, minor = True)
    # ax.grid(which='minor')#, color='k', alpha=0.2)
    # # ax.grid()
    #
    # plt.show()
    # input()

    ##

