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
from py_logs import get_logger
logger = get_logger(__name__)
from multiprocess import Pool
if __name__ == '__main__':
    ## Parameters

    Ni = 3
    Nj = 3

    Ncul = 3

    iz = range(Ni)
    jz = range(Nj)

    coords0 = [[i, j] for i in iz for j in jz]

    path_tetris = '/home/chilly-ben/Documents/Créations/Code/tiwanaku/tetris_forms.json'
    with open(path_tetris, "r") as fp:
        tetris_forms = json.load(fp)

    start = time.time()

    ## Functions


    def fun_big_neighbors(ter):
        i, j = ter
        return [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]]


    def fun_forms_in_remaining(i,j, remaining_ters, size_reg):
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


    def rec_form(remaining_ters0, list_forms0, list_boards0, impossibilities0, cultures0, region):
        list_forms = copy.deepcopy(list_forms0)
        list_boards = copy.deepcopy(list_boards0)
        impossibilities = copy.deepcopy(impossibilities0)
        cultures = copy.deepcopy(cultures0)
        if not list_forms:
            # logger.debug(region)
            print(region, time.time()-start)

        bool_pos = True
        for cult in range(1, len(region)+1):
            impos_tmp = coords0.copy()
            count = 0
            for i,j in region:
                if cult not in impossibilities[i][j]:
                    cult_tmp = cult
                    count += 1
                    neighbors = fun_big_neighbors([i,j])
                    impos_tmp = [ter for ter in impos_tmp if ter in neighbors]
            if count == 0:
                bool_pos = False
                break
            elif count == 1:
                cultures[i][j] = cult_tmp
            for i,j in impos_tmp:
                # print(i,j)
                if cult not in impossibilities[i][j]:
                    impossibilities[i][j].append(cult)
        if bool_pos:
            if region:
                list_forms.append(region)
            remaining_ters = [ter for ter in remaining_ters0 if ter not in region]
            if not remaining_ters:
                # print(list_forms)
                list_boards.append([list_forms, cultures])
            else:
                i,j = remaining_ters[0]
                for size_reg in range(1,Ncul+1):
                    possible_forms = fun_forms_in_remaining(i,j, remaining_ters, size_reg)
                    for region in possible_forms:
                        list_boards = rec_form(remaining_ters, list_forms, list_boards, impossibilities, cultures, region)
        # print()
        return list_boards

    cultures0 = [[[] for j in jz] for i in iz]
    impossibilities0 = cultures0.copy()
    # region = []
    remaining_ters0 = coords0.copy()
    list_forms0 = []
    list_boards0 = []

    first_forms = []
    for size_reg in range(1,Ncul+1):
        first_forms.extend(fun_forms_in_remaining(0,0, remaining_ters0, size_reg))

##

    lis = []

    # for region in first_forms:
    #     lis.extend(rec_form(remaining_ters0, list_forms0, list_boards0, impossibilities0, cultures0, region))

    p = Pool(7)
    results = p.map(partial(rec_form, remaining_ters0, list_forms0, list_boards0, impossibilities0, cultures0), first_forms)
    # p.close()
    # p.join()
    for res in results:
        lis.extend(res)

    ##

    print(len(lis))
    # for sol,_ in lis:
    #     print(sol)

    # with open('/home/chilly-ben/Documents/Créations/Code/tiwanaku/solution_forms.json', "w") as fp:
    #     json.dump(lis, fp)

    ##

    if 0:
        for ind in range(len(lis)):
        # ind = randrange(len(lis))

            list_regions = lis[ind][0]
            list_sorted0 = sorted(list_regions, key = len)

        # ############### Find possible cultures (inner function)


            def rec_mini(list_region0, culture, cul_remaining0, region, list_lists0, ind, impossibilities):
                list_region = list_region0.copy()
                cul_remaining = cul_remaining0.copy()
                list_lists = list_lists0.copy()
                if culture:
                    list_region.append(culture)
                    cul_remaining.remove(culture)

                if len(list_region) == len(region):
                    list_lists.append(list_region)

                else:
                    i,j = region[ind]
                    poss_tmp = [culture for culture in cul_remaining if culture not in impossibilities[i][j]]
                    for culture in poss_tmp:
                        list_lists = rec_mini(list_region, culture, cul_remaining, region, list_lists, ind+1, impossibilities)

                return list_lists


        # ############### Find possible cultures (outer function)


            def rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind):
                solution = solution0.copy()
                impossibilities = copy.deepcopy(impossibilities0)
                list_solutions = list_solutions0.copy()

                if cult_region:
                    solution.append(cult_region)

                if len(solution) == len(list_regions):
                    list_solutions.append(solution)

                else:

                    if cult_region:
                        region = list_regions[ind-1]
                        for ind_reg, cult in enumerate(cult_region):
                            i,j = region[ind_reg]
                            neighbors = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords0]
                            for a,b in neighbors:
                                if cult not in impossibilities[a][b]:
                                    impossibilities[a][b].append(cult)

                    region = list_regions[ind]
                    list_cult_region = rec_mini([], [], cultures_types[len(region)-1], region, [], 0, impossibilities)
                    for cult_region in list_cult_region:
                        list_solutions = rec_maxi(solution, impossibilities, list_solutions, cult_region, list_regions, ind+1)

                return list_solutions

            cultures_types = [[i+1 for i in range(size)] for size in range(1,6)]
            solution0 = []
            impossibilities0 = [[[] for j in jz] for i in iz]
            # impossibilities0 = [[[] for i in iz] for j in jz]
            list_solutions0 = []
            cult_region = []
            list_regions = list_sorted0.copy()
            # list_regions = [[[0, 0], [0, 1], [1,0]], [[0,2], [0,3], [1, 2]]]
            ind = 0

            list_solutions = rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind)
            if list_solutions:
                print(list_regions)
                print(list_solutions)
                input()

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

