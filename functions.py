'''

'''
import time
from random import randrange, choice, shuffle
import numpy as np
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


def fun_neighbors_all(global_var, tetris_forms):
    ''' All tetris forms for each territory i,j and size '''
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
    regs_ij = [[[[] for size in range(size_max_reg)] for j in jz] for i in iz]
    for i in iz:
        for j in jz:
            for size in range(size_max_reg):
                regs_all_ij = [[[a+i,b+j] for a,b in reg] for reg in tetris_forms[size]]
                for reg in regs_all_ij:
                    for ter in reg:
                        if ter not in coords_all:
                            break
                    else: # no break: region is inside board
                        regs_ij[i][j][size].append(reg)
    return regs_ij


## Generation of cultures

def put_numbers(global_var):
    '''
    Start computations by filling boards with numbers (= cultures = crops),
    following the only rule of two same crops cannot be next to one another.
    The board is filled with crops with increasing value.
    Each value is put a random number of times, number between dependant bounds.
    As soon as there is an impossibility, start over.
    The largest crops are done in the end, as they should merely fill the remaining holes.
    '''
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var

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
                    break # leave loop over ind

            # If loop stopped, at least Nmin crops ?
            nb_cult = len(list_per_cults[crop-1])
            if nb_cult < Nmin:
                bol = False
                break # leave loop over crop

            Ns[crop-1] = nb_cult
            Nmax = nb_cult # For next crop, there must be at most as much as this one
            Nsofar = sum(Ns)
            Nmin = int((NN - Nsofar)/size_max_reg) + 1 # so that the biggest 5 regions can fill the board

            if Nmin > Nmax:
                bol = False
                break # leave loop over crop

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
                        break # leave loop over a,b

                    list_cultures[a,b] = crop
                    list_per_cults[crop-1].append([a,b])
                    impossibilities = fun_update_small(a,b, crop, impossibilities, coords_all)

            else:
                bol = False
    return compteur, Ns, list_cultures, list_per_cults, impossibilities


## Associated regions


def put_regions(global_var, Ns, list_per_cults, list_cultures, regs_ij):
    '''
    Fitting regions into the board already filled with cultures.
    Regions are put by decreasing size, each starting on any crop corresponding to its size.
    As soon as there is an impossibility, start over.
    Except if it is shown that a territory is part of no valid region, considering the current crops.
    In this case, start over to put_numbers function.
    '''
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var

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
    while 1:
        compt += 1
        poss = np.ones((Ni,Nj))
        list_regs = []

        list_per_cults_copy = copy.deepcopy(list_per_cults)
        for size in Nsizes_list:
            # Choose a territory with the current region's maximal crop
            i,j = choice(list_per_cults_copy[size-1])
            seti = set(range(1,size+1))

            # Find a region of size size, containing i,j, in the remaining available board
            all_regs = regs_ij[i][j][size-1]
            shuffle(all_regs)
            bol_impos = True
            bol_reg = False
            for reg in all_regs:

                if set([list_cultures[a,b] for a,b in reg]) == seti:
                    # There exists a region fitting the board and its cultures
                    bol_impos = False

                    for a,b in reg:
                        if not poss[a,b]:
                            break # leave loop over reg
                    else: # no break: valid region
                        bol_reg = True
                        break # leave loop over all_regs

            # Impossibility to solve board with these cultures
            if bol_impos:
                # Leave function and go back to generating new cultures
                return compt, 0, 0, bol_impos

            if bol_reg:
            # Updating variables with new valid region
                list_regs.append(reg)
                for a,b in reg:
                    poss[a,b] = 0
                    list_per_cults_copy[list_cultures[a,b]-1].remove([a,b])
            else:
            # Start over filling the board
                break # leave loop over Nsizes_list


        else: # no break: board filled with regions
            break # leave while loop

    # Formatting solutions
    list_regs.reverse()
    # list_regs = sorted(list_regs, key = len)

    board = np.full((Ni,Nj),0)
    for ind, reg in enumerate(list_regs):
        for i,j in reg:
            board[i,j] = ind+1

    return compt, list_regs, board, False


## Possible colors set


def put_colors(global_var, sorted_regs, board):
    '''
    Associate each region with a color, following the rule that
    two adjacent regions cannot have the same color.
    Regions with the fewest possible colors are colored first.
    As soon as there is an impossibility, start over,
    although so far the solution has always been found during the first try.
    '''
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var

    bol_no = True
    compt = 0
    while bol_no:
        compt += 1

        impossibilities = [set() for _ in range(len(sorted_regs))]
        arr_cols = np.full((Ni,Nj),0)
        # Variable checking if the Ncols colors are used at least once
        cols_used = set()
        for _ in sorted_regs: # number of iterations must be the number of regions

            # Select region the most constrained in color
            maxi = 0
            ind_worst_reg = 0
            mini_bol = False
            for ind, nocols in enumerate(impossibilities):
                leni = len(nocols)

                if leni == Ncols:
                    # No possible color for one region
                    mini_bol = True
                    break # exit loop over nocols

                elif leni > maxi:
                    maxi = leni
                    ind_worst_reg = ind

            else: # no break:
                reg = sorted_regs[ind_worst_reg]
                coords_others = [ter for ter in coords_all if ter not in reg]
                cols = list(colors_set - impossibilities[ind_worst_reg])
                col = choice(cols) # a random color is chosen
                cols_used.add(col)
                impossibilities[ind_worst_reg] = set() # so that this region is not chosen again

                for i,j in reg:
                    # Fill solution array with colors
                    arr_cols[i,j] = col
                    # Update impossible colors in adjacent regions
                    for neigh in [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]]:
                        if neigh in coords_others and not arr_cols[neigh[0], neigh[1]]: # ensure regions already filled are not considered anymore
                            impossibilities[board[neigh[0], neigh[1]]-1].add(col)

            if mini_bol:
                break # exit loop over sorted_regs

        else: # no break:
            bol_no = len(cols_used) != Ncols

    return arr_cols

## All solutions corresponding to these regions


def init_rec(global_var, sorted_regs, board):
    ''' Initialize variables for the recursive function '''
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
    solution0 = []
    list_solutions0 = []
    cult_region = []
    list_regions = sorted_regs
    ind = 0

    # Crops larger than the size of a region are considered in the impossibilites
    impossibilities0 = [[set() for j in jz] for i in iz]
    for i in iz:
        for j in jz:
            leni = len(sorted_regs[board[i,j]-1])
            impossibilities0[i][j] = set(range(leni+1,size_max_reg+1))

    return solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind


def rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind, permuts, coords_all):
    '''
    Find all solutions corresponding to the regions found by function put_regions.
    Each call of this recursive function fills a region with crops, starting with the largest regions.

    Recursion functions work as follows:
    - make a copy of lists to be updated
    - update lists
    - condition of end of recursion
    - recursion: loops on diverging possibilities
    '''
    # Copying...
    solution = solution0.copy()
    impossibilities = copy.deepcopy(impossibilities0)
    list_solutions = list_solutions0.copy()

    # If a region was passed on (always, except for first call), add it to the current solution
    if cult_region:
        solution.append(cult_region)

    # When current solution is complete, add it to the list
    if len(solution) == len(list_regions):
        list_solutions.append(solution)

    else:

        # If new region is added, update the impossibilities
        # The impossibilities of the given region are also updated for the fill_impos function
        if cult_region:
            region = list_regions[ind-1]
            coords = [ter for ter in coords_all if ter not in region]
            for ind_reg, cult in enumerate(cult_region):
                i,j = region[ind_reg]
                neighbors = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords]
                for a,b in neighbors+region: # some region members may not be adjacent
                    if [a,b]!=[i,j]:
                        impossibilities[a][b].add(cult)

        ''' In progress (see important/faster_solve scripts): acceleration by logic solving at each step. Can be uncommented. '''
        # _, impossibilities = fill_impos(impossibilities, sorted_regs, board)

        region = list_regions[ind]
        # For all permutationso of cultures of the right size...
        for cult_region in permuts[len(region)-1]:

            # Check if this combination of cultures is possible
            for ind_cult, cult in enumerate(cult_region):
                a,b = region[ind_cult]
                if cult in impossibilities[a][b]:
                    break # terminate computations from the first impossibility
            else: # no break: this combination is possible
                # Recursive call, by incrementing the region index
                list_solutions = rec_maxi(solution, impossibilities, list_solutions, cult_region, list_regions, ind+1, permuts, coords_all)

    return list_solutions


## Initialize board with unique solution


def init_board(global_var, sorted_regs, list_solutions, Nsol, list_cultures, arr_cols):
    '''
    Find a set of territories which, when their crop is revealed, leads to
    the initial solution, found by the put_numbers function.
    This is done by finding the territories where there are few solutions having
    the same crop than the initial one.
    '''
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
    # Convert format of list of solutions
    array_solutions = np.full((Nsol, Ni, Nj), 0)
    for ind_sol in range(Nsol):
        for ind_reg, reg in enumerate(sorted_regs):
            for ind_ter, ter in enumerate(reg):
                array_solutions[ind_sol, ter[0], ter[1]] = list_solutions[ind_sol][ind_reg][ind_ter]

    # Find necessary information leading to the crops first found by put_numbers function
    bol0 = True
    inds = set(range(Nsol)) # Solutions which can still be obtained by minimal board
    unique = np.full((Ni,Nj), 0) # Minimal board leading to solution
    while bol0:
        # For each territory, number of solutions having the same crop as the initial solution
        nbs = np.full((Ni,Nj), 0)
        for ind_sol in inds:
            nbs += (array_solutions[ind_sol,:,:] == list_cultures)
        # Consider the territory corresponding to the fewest solutions
        i,j = np.unravel_index(np.argmin(nbs), nbs.shape)
        unique[i,j] = list_cultures[i,j]
        # Updates remaining solutions
        inds = set([ind for ind in inds if array_solutions[ind,i,j]==list_cultures[i,j]])
        bol0 = (len(inds) > 1)

    # Data to print when bol_interaction (df0 = whole solution, df = solution in progress)
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
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
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
    Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set = global_var
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