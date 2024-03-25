'''

'''
import time
from random import randrange, choice, shuffle
import numpy as np
import json
import copy
import pandas as pd
from tabulate import tabulate
from itertools import permutations
from operator import itemgetter
## General


def fun_update_small(i,j, cult, impossibilities, coords_all):
    neighbors = fun_neighbors(i,j)
    impos_tmp = [ter for ter in neighbors if ter in coords_all] # neighbors which are on the list_cultures
    for a,b in impos_tmp: # i,j could be re-used
        impossibilities[a,b] = cult
    return impossibilities


def fun_neighbors(i,j):
    ''' Coordinates of all 8 neighbors of terrain [i,j] '''
    return [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]] # list also contains ter, which is not a problem


def fun_time(start):
    time_format = '%H:%M:%S'
    med = time.time()
    Nseconds = int(med-start)
    elapsed_time = str(time.strftime(time_format, time.gmtime(Nseconds)))
    print('Duration =', elapsed_time)
    return med


def fun_permut(size_max_reg):
    ''' All possible sequences of cultures, for all region sizes '''
    permuts = []
    for size in range(1, size_max_reg+1):
        permuts.append([[ind for ind in permut] for permut in permutations(range(1,size+1))]) # permutations function yields tuples
    return permuts


##

def put_numbers(global_var):
    Ni, Nj, NN, size_max_reg, coords_all = global_var
    Ns = np.full((size_max_reg,),0)
    bol = False
    compteur = 0
    while not bol:
        compteur += 1
        bol = True
        Nmin = Nj
        Nmax = 2*Nj
        list_cultures = np.full((Ni,Nj),0)
        list_per_cults = [[] for _ in range(size_max_reg)]
        impossibilities = np.zeros((Ni, Nj))
        for crop in range(1, size_max_reg):
            N = randrange(Nmin, Nmax+1)

            ind = 0
            while ind < N:
                possib = [[i,j] for i,j in coords_all if not impossibilities[i,j]]
                if possib:
                    a,b = choice(possib)
                    list_cultures[a,b] = crop
                    list_per_cults[crop-1].append([a,b])
                    impossibilities = fun_update_small(a,b, crop, impossibilities, coords_all)
                    ind += 1
                else:
                    break
            if ind < Nmin:
                bol = False
                break

            Ns[crop-1] = ind
            Nmax = ind
            Nsofar = sum(Ns)
            Nmin = int((NN - Nsofar)/size_max_reg) + 1

            if Nmin > Nmax:
                bol = False
                break

            impossibilities = 1.*list_cultures

        #

        if bol:
            remainings = [[i,j] for i,j in coords_all if not list_cultures[i,j]]
            if len(remainings) <= Ns[-2]:
                crop = size_max_reg
                for a,b in remainings:
                    if impossibilities[a,b]:
                        bol = False
                        break
                    list_cultures[a,b] = crop
                    list_per_cults[crop-1].append([a,b])
                    impossibilities = fun_update_small(a,b, crop, impossibilities, coords_all)
            else:
                bol = False
    return compteur, Ns, list_cultures, list_per_cults, impossibilities


##


def put_regions(global_var, Ns, list_per_cults, list_cultures):
    path_tetris, NN, Ni, Nj, coords_all = global_var

    # All possible region forms
    with open(path_tetris, "r") as fp:
        tetris_forms = json.load(fp)

    Ns[-1] = NN - sum(Ns[:-1])
    Nsizes = [Ns[i]-Ns[i+1] for i in range(len(Ns)-1)] + [Ns[-1]]

    Nsizes_list = []
    for ind, Nsize in enumerate(Nsizes):
        Nsizes_list.extend(Nsize*[ind+1])
    Nsizes_list.reverse()

    compt = 0
    bol_filled = True
    while bol_filled:
        compt += 1
        poss = np.ones((Ni,Nj))
        # board = np.full((Ni,Nj),0)
        list_regs = []

        bol_filled = True
        ind_reg = 1
        # while bol_filled:
        list_per_cults_copy = copy.deepcopy(list_per_cults)
        # shuffle(Nsizes_list)
        for size in Nsizes_list:

            i,j = choice(list_per_cults_copy[size-1])
            # i,j = np.unravel_index(np.argmax(list_cultures*poss), list_cultures.shape)
            # size = list_cultures[i,j]
            seti = set(range(1,size+1))

            all_regs = [[[a+i,b+j] for a,b in reg] for reg in tetris_forms[size-1]]
            shuffle(all_regs)
            for reg in all_regs:
                for a,b in reg:
                    if ([a,b] not in coords_all) or (not poss[a,b]):
                        break
                else:
                    if set([list_cultures[a,b] for a,b in reg]) == seti:
                        break
            else:
                break

            list_regs.append(reg)
            for a,b in reg:
                # board[a,b] = ind_reg
                poss[a,b] = 0
                list_per_cults_copy[list_cultures[a,b]-1].remove([a,b])

            for a,b in coords_all:
                if poss[a,b]:
                    ind_reg += 1
                    break
            else:
                bol_filled = False

    sorted_regs = sorted(list_regs, key = len)

    board = np.full((Ni,Nj),0)
    for ind, reg in enumerate(sorted_regs):
        for i,j in reg:
            board[i,j] = ind+1

    return compt, sorted_regs, board


##


def put_colors(global_var, sorted_regs, board):
    Ni, Nj, Ncols, colors_set, coords_all = global_var
    Nreg = len(sorted_regs)

    bol_no = True
    compt = 0
    while bol_no:
        compt += 1

        impossibilities = [set() for _ in range(Nreg)]
        arr_cols = np.full((Ni,Nj),0)
        cols_used = set()
        for _ in sorted_regs:

            maxi = 0
            ind_worst_reg = 0
            mini_bol = False
            for ind, nocols in enumerate(impossibilities):
                leni = len(nocols)
                if leni == Ncols:
                    mini_bol = True
                    break
                elif leni > maxi:
                    maxi = leni
                    ind_worst_reg = ind

            else:
                reg = sorted_regs[ind_worst_reg]
                cols = list(colors_set - impossibilities[ind_worst_reg])
                col = choice(cols)
                cols_used.add(col)
                impossibilities[ind_worst_reg] = set()

                neighs = []
                coords_others = [ter for ter in coords_all if (ter not in reg) and (ter not in neighs)]
                for i,j in reg:
                    arr_cols[i,j] = col

                    for neigh in [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]]:
                        if neigh in coords_others and not arr_cols[neigh[0], neigh[1]]:
                            impossibilities[board[neigh[0], neigh[1]]-1].add(col)
                            neighs.append(neigh)
            if mini_bol:
                break
        else:
            if len(cols_used) == Ncols:
                bol_no = False

    return arr_cols

##


def init_rec(global_var, sorted_regs, board):
    size_max_reg, iz, jz, coords_all = global_var
    # cultures_types = [[i+1 for i in range(size)] for size in range(1,size_max_reg+1)]
    solution0 = []
    list_solutions0 = []
    cult_region = []
    list_regions = sorted_regs
    ind = 0

    # neighbors_all = [[[] for j in jz] for i in iz]
    # for i in iz:
    #     for j in jz:
    #         reg = sorted_regs[board[i,j]-1]
    #         coords = [ter for ter in coords_all if ter not in reg]
    #         neighbors_all[i][j] = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords]

    impossibilities0 = [[set() for j in jz] for i in iz]
    for i in iz:
        for j in jz:
            leni = len(sorted_regs[board[i,j]-1])
            impossibilities0[i][j] = set(range(leni+1,size_max_reg+1))

    return solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind


def rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind, global_var):
    permuts, coords_all = global_var
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
            coords = [ter for ter in coords_all if ter not in region]
            for ind_reg, cult in enumerate(cult_region):
                i,j = region[ind_reg]
                neighbors = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords]
                for a,b in neighbors+region:
                    if cult not in impossibilities[a][b] and [a,b]!=[i,j]:
                        impossibilities[a][b].add(cult)

        ''' acceleration by logic solving at each step '''
        # _, impossibilities = fill_impos(impossibilities, sorted_regs, board)

        region = list_regions[ind]

        for cult_region in permuts[len(region)-1]:
            for ind_cult, cult in enumerate(cult_region):
                a,b = region[ind_cult]
                if cult in impossibilities[a][b]:
                    break # terminate computations from the first impossibility
            else: # if no break
                list_solutions = rec_maxi(solution, impossibilities, list_solutions, cult_region, list_regions, ind+1, global_var)


        # list_cult_region = rec_mini([], [], cultures_types[len(region)-1], region, [], 0, impossibilities)
        # for cult_region in list_cult_region:
        #     list_solutions = rec_maxi(solution, impossibilities, list_solutions, cult_region, list_regions, ind+1)

    return list_solutions


def fill_impos(impos, sorted_regs, board):
# if 1:
    ''' Tant qu'il y a des régions qui ont subi des modifications... '''
    list_modif = list(range(len(sorted_regs)))
    while list_modif:
        ind_reg = list_modif[0]
        set0 = set(list_modif)
        set0.remove(ind_reg)
        reg = sorted_regs[ind_reg]

        ''' Pour la région courante, liste des voisins à modifier pour chaque culture '''
        neigh_cult = [[] for _ in cults]
        bool_cult = size_max_reg*[0]
        for i,j in reg:
            neighbors = neighbors_all[i][j]
            for cult in cults:
                if cult not in impos[i][j]:
                    if bool_cult[cult-1]:
                        neigh_cult[cult-1] = [ter for ter in neighbors if ter in neigh_cult[cult-1]]
                    else:
                        neigh_cult[cult-1] = neighbors
                        bool_cult[cult-1] = 1

        ''' Modification de ces voisins '''
        set_tmp = set()
        for ind_cult, list_news in enumerate(neigh_cult):
            for i,j in list_news:
                cult = ind_cult+1
                if cult not in impos[i][j]:
                    ind_reg = board[i,j]-1
                    set_tmp.add(ind_reg)
                    impos[i][j].add(cult)
                    if len(impos[i][j]) == size_max_reg:
                        return True, impos

        ''' Actualiser régions modifiées si impos rempli dans une case '''
        for ind_reg in set_tmp:
            reg_tmp = sorted_regs[ind_reg].copy()
            for _ in range(len(sorted_regs[ind_reg])):
                lens = [len(impos[i][j]) for i,j in reg_tmp]
                ind_maxi, maxi = max(enumerate(lens), key=itemgetter(1))
                if maxi == size_max_reg-1:
                    x,y = reg_tmp[ind_maxi]
                    reg_tmp.remove([x,y])
                    cult_tmp = list(set_max - impos[x][y])[0]
                    for a,b in reg_tmp:
                        impos[a][b].add(cult_tmp)
                        if len(impos[a][b]) == size_max_reg:
                            return True, impos
                else:
                    break

        ''' Actualiser régions modifiées si impos rempli pour une culture '''
        for ind_reg in set_tmp:
            reg_tmp = sorted_regs[ind_reg].copy()
            range_tmp = range(1,len(reg_tmp)+1)

            for cult in range_tmp:
                ters = [[i,j] for i,j in reg_tmp if cult not in impos[i][j]]
                if len(ters) == 1:
                    i,j = ters[0]
                    impos[i][j] = sets[cult-1]
                    # if len(impos[i][j]) == size_max_reg:
                    #     return True, impos

        list_modif = list(set_tmp | set0)
    return False, impos


# def rec_mini(list_region0, culture, cul_remaining0, region, list_lists0, ind, impossibilities):
#     list_region = list_region0.copy()
#     cul_remaining = cul_remaining0.copy()
#     list_lists = list_lists0.copy()
#     if culture:
#         list_region.append(culture)
#         cul_remaining.remove(culture)
#
#     if len(list_region) == len(region):
#         list_lists.append(list_region)
#
#     else:
#         i,j = region[ind]
#         poss_tmp = [culture for culture in cul_remaining if culture not in impossibilities[i][j]]
#         for culture in poss_tmp:
#             list_lists = rec_mini(list_region, culture, cul_remaining, region, list_lists, ind+1, impossibilities)
#
#     return list_lists

##

def init_board(global_var, sorted_regs, list_solutions, list_cultures, arr_cols):
    Ni, Nj, iz, jz, path_df0, path_df, colors_small = global_var
    Nsol = len(list_solutions)
    array_solutions = np.full((Nsol, Ni, Nj), 0)
    for ind_sol in range(Nsol):
        for ind_reg, reg in enumerate(sorted_regs):
            for ind_ter, ter in enumerate(reg):
                array_solutions[ind_sol, ter[0], ter[1]] = list_solutions[ind_sol][ind_reg][ind_ter]

    bol0 = True
    inds = set(range(Nsol))
    unique = np.full((Ni,Nj), 0)
    while bol0:

        nbs = np.full((Ni,Nj), 0)
        for ind_sol in inds:
            nbs += (array_solutions[ind_sol,:,:] == list_cultures)

        i,j = np.unravel_index(np.argmin(nbs), nbs.shape)
        unique[i,j] = list_cultures[i,j]

        inds = set([ind for ind in inds if array_solutions[ind,i,j]==list_cultures[i,j]])
        bol0 = (len(inds) > 1)

    df0 = pd.DataFrame(list_cultures)
    df = df0.copy()
    for i in iz:
        for j in jz:
            ind_col = arr_cols[i,j]-1
            df0[j][i] = colors_small[ind_col] + ' ' +  str(df0[j][i])
            if not int(unique[i,j]):
                df[j][i] = ''
            else:
                df[j][i] = df0[j][i]

    np.save(path_df0, df0.values)
    np.save(path_df, df.values)
    return df0, df