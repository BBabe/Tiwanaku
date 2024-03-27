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
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
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
    '''
    Start computations by filling boards with numbers (= cultures = crops),
    following the only rule of two same crops cannot be next to one another.
    Regions will be fitted into this filled board only after (with high probability).
    This appears to be way much faster than my original method, which consisted in
    iteratively filling the board with filled regions compatible with existing board
    (see important/old_all_solutions_functions.py)
    '''
    Ni, Nj, path_df, path_df0, path_tetris, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var

    Ns = np.full((size_max_reg,),0)
    # Information on number of tests
    compteur = 0
    bol = False
    # Loop until solution found
    while not bol:
        compteur += 1
        # bol is set as False as soon as the current board filling fails
        bol = True

        # Initialization
        Nmin = Nj # Maximum number of regions of size size_max_reg
        Nmax = 2*Nj # Arbitrary number, in practice is always less --> optimization ?
        list_cultures = np.full((Ni,Nj),0) # solution in array
        list_per_cults = [[] for _ in range(size_max_reg)] # solution in list ???
        impossibilities = np.zeros((Ni, Nj))

        # Add crops (= cultures) on board, in increasing order, up to size_max_reg-1 !
        for crop in range(1, size_max_reg):
            N = randrange(Nmin, Nmax+1)

            for ind in range(N):
                possib = [[i,j] for i,j in coords_all if not impossibilities[i,j]]
                if possib: # to use choice function
                    a,b = choice(possib)
                    list_cultures[a,b] = crop
                    list_per_cults[crop-1].append([a,b])
                    impossibilities = fun_update_small(a,b, crop, impossibilities, coords_all) # [a,b] in its own neighborhood
                else:
                    break

            # If loop stopped, at least Nmin crops ?
            nb_cult = len(list_per_cults[crop-1])
            if nb_cult < Nmin:
                bol = False
                break

            Ns[crop-1] = nb_cult
            Nmax = nb_cult # For next crop, there must be at most as much as this one
            Nsofar = sum(Ns)
            Nmin = int((NN - Nsofar)/size_max_reg) + 1 # so that the biggest 5 regions can fill the board

            if Nmin > Nmax:
                bol = False
                break

            # Already filles territories won't be a second time
            impossibilities = 1.*list_cultures

        # Add crops of value size_max_reg
        if bol:
            remainings = [[i,j] for i,j in coords_all if not list_cultures[i,j]]
            # In order to have at most as much of these crops as the size_max_reg-1 crops
            if len(remainings) <= Ns[-2]:
                crop = size_max_reg
                for a,b in remainings:
                    # Test not for first iteration, when impossibilities = list_cultures
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
    '''

    '''
    Ni, Nj, path_df, path_df0, path_tetris, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var

    # All possible region forms (some 5 regions are impossible in this game, when U or L form)
    with open(path_tetris, "r") as fp:
        tetris_forms = json.load(fp)

    Ns[-1] = NN - sum(Ns[:-1])
    # Number of regions of each size
    Nsizes = [Ns[i]-Ns[i+1] for i in range(len(Ns)-1)] + [Ns[-1]]
    # Repeat n times each number n
    Nsizes_list = []
    for ind, Nsize in enumerate(Nsizes):
        Nsizes_list.extend(Nsize*[ind+1])
    # After some tests, starting with biggest regions invalidates current solution sooner
    Nsizes_list.reverse()

    compt = 0
    bol_filled = False
    bol_impos = False
    while (not bol_filled) and (not bol_impos):
        compt += 1
        poss = np.ones((Ni,Nj))
        list_regs = []

        list_per_cults_copy = copy.deepcopy(list_per_cults)
        for size in Nsizes_list:
            # Choose a territory with the current region's maximal crop
            i,j = choice(list_per_cults_copy[size-1])
            seti = set(range(1,size+1))

            # Find a region of size size, containing i,j, in the remaining available board
            all_regs = [[[a+i,b+j] for a,b in reg] for reg in tetris_forms[size-1]] # pre-compute tetris_forms for each i,j, to get rid of coords_all's test ?
            shuffle(all_regs)
            for reg in all_regs:
                for a,b in reg:
                    if ([a,b] not in coords_all) or (not poss[a,b]):
                        break
                else: # break
                    if set([list_cultures[a,b] for a,b in reg]) == seti:
                        break
            else:     # break
                bol_impos = True
                break

            list_regs.append(reg)
            for a,b in reg:
                poss[a,b] = 0
                list_per_cults_copy[list_cultures[a,b]-1].remove([a,b])

            for a,b in coords_all:
                if poss[a,b]:
                    break
            else:
                bol_filled = True

    sorted_regs = sorted(list_regs, key = len)

    board = np.full((Ni,Nj),0)
    for ind, reg in enumerate(sorted_regs):
        for i,j in reg:
            board[i,j] = ind+1

    return compt, sorted_regs, board, bol_impos


##


def put_colors(global_var, sorted_regs, board):
    Ni, Nj, path_df, path_df0, path_tetris, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
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
    Ni, Nj, path_df, path_df0, path_tetris, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
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


def rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind, permuts, coords_all):
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
                list_solutions = rec_maxi(solution, impossibilities, list_solutions, cult_region, list_regions, ind+1, permuts, coords_all)

    return list_solutions


##

def init_board(global_var, sorted_regs, list_solutions, Nsol, list_cultures, arr_cols):
    Ni, Nj, path_df, path_df0, path_tetris, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
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

##

def interaction(global_var, df0, df):
    Ni, Nj, path_df, path_df0, path_tetris, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
    Ntuiles = np.full((Ncols,), 0)
    for i in iz:
        for j in jz:
            ind_col = colors_small.index(df0[j][i][0])
            Ntuiles[ind_col] += 1

    #
    while 1:
        remain_tmp = ''
        for ind in range(Ncols):
            remain_tmp += ' {} = {} '.format(colors_small[ind], Ntuiles[ind])
        print(tabulate(df.values, tablefmt='grid'))
        print(remain_tmp, '(remaining terrains)')
        print()
        typ = int(input('Which type ? (0 = Color ; 1 = Number)  '))
        print()

        print('Where ?')
        i = int(input('i = '))
        j = int(input('j = '))
        print()

        col = df0[j][i][0]
        ind_col = colors_small.index(col)
        if not df[j][i]:
            Ntuiles[ind_col] -= 1
        num = df0[j][i][-1]
        # num = list_cultures[i,j]
        if typ == 0:
            df[j][i] = col
            print(df[j][i])
        elif typ == 1:
            df[j][i] = col + ' ' +  str(num)
            print('ANSWER =', df[j][i])
        np.save(path_df, df)


def fun_plot(global_var, list_solutions, Nsol, arr_cols, sorted_regs):
    Ni, Nj, path_df, path_df0, path_tetris, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
    ft = 40
    ind = int(input('Which solution to plot, between 0 and {}? '.format(Nsol-1)))
    sol_list = list_solutions[ind]
    sol_array = np.full((Ni, Nj), 0)
    for ind_reg, sol_reg in enumerate(sol_list):
        reg = sorted_regs[ind_reg]
        for ind_ter, cult in enumerate(sol_reg):
            i,j = sorted_regs[ind_reg][ind_ter]
            sol_array[i,j] = sol_list[ind_reg][ind_ter]

    plt.close('all')

    minor_y = np.arange(0.5, Ni-1)
    minor_x = np.arange(0.5, Nj-1)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    cmap = ListedColormap(colors)
    ax.imshow(arr_cols, cmap = cmap)

    ax.set_xticks(minor_x, [])
    ax.set_yticks(minor_y, [])
    ax.grid(True)

    for i in iz:
        for j in jz:
            text = ax.text(j, i, sol_array[i,j],ha="center", va="center", color="k", fontsize=ft)

    plt.show()

##

# # Set of possible cultures
# set_max = set(range(1, size_max_reg+1))
# # All cultures except one
# sets = [set_max - set([ind]) for ind in set_max]
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


        # list_cult_region = rec_mini([], [], cultures_types[len(region)-1], region, [], 0, impossibilities)
        # for cult_region in list_cult_region:
        #     list_solutions = rec_maxi(solution, impossibilities, list_solutions, cult_region, list_regions, ind+1, permuts, coords_all)

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