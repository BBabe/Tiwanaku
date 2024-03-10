import time
from random import randrange, choice, shuffle
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from operator import itemgetter
import copy
import pandas as pd
from tabulate import tabulate
## Input parameters

# Number of lines
Ni = 5
# Number of columns
Nj = 5
# Maximal region size
size_max_reg = 5

##

NN = Ni*Nj
iz = range(Ni)
jz = range(Nj)
# All terrains coordinates
coords_all = [[i, j] for i in iz for j in jz]

##

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

##

print('Generation of cultures...')
start = time.time()
Ns = np.full((size_max_reg,),0)

bol = False
compteur = 0
while not bol:
    compteur += 1
    # print(compteur)
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


    #

    # input(list_cultures)
print('Number of tests =', compteur)
# print(list_cultures)

Ns[-1] = NN - sum(Ns[:-1])
Nsizes = [Ns[i]-Ns[i+1] for i in range(len(Ns)-1)] + [Ns[-1]]
print('Number of regions of size', list(range(1, size_max_reg+1)), '=', Nsizes)

start = fun_time(start)
print()

##

# All possible region forms
with open('data/tetris_forms.json', "r") as fp:
    tetris_forms = json.load(fp)

##

print('Associated regions...')
Nsizes_list = []
for ind, Nsize in enumerate(Nsizes):
    Nsizes_list.extend(Nsize*[ind+1])
Nsizes_list.reverse()

# Nexp = 20
# arr_exp = np.zeros((3,Nexp))
# for ind_exp in range(Nexp):
#     print(ind_exp)
#     start = time.time()


compt = 0
bol_filled = True
while bol_filled:
    compt += 1
    poss = np.ones((Ni,Nj))
    board = np.full((Ni,Nj),0)
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
            board[a,b] = ind_reg
            poss[a,b] = 0
            list_per_cults_copy[list_cultures[a,b]-1].remove([a,b])

        for a,b in coords_all:
            if poss[a,b]:
                ind_reg += 1
                break
        else:
            bol_filled = False


#     arr_exp[0,ind_exp] = time.time() - start
#     arr_exp[1,ind_exp] = compt
#     arr_exp[2,ind_exp] = compt / arr_exp[0,ind_exp]
#     print(arr_exp[:,ind_exp])
# print()
# print(np.mean(arr_exp, axis = 1))

print('Number of tests =', compt)
start = fun_time(start)
print()

sorted_regs = sorted(list_regs, key = len)

##

board = np.full((Ni,Nj),0)
for ind, reg in enumerate(sorted_regs):
    for i,j in reg:
        board[i,j] = ind+1

##

print('Possible colors set...')
# colors = ['brown', 'yellow', 'green', 'blue']
colors = ['peru', 'gold', 'limegreen', 'steelblue']
colors_small = ['M', 'J', 'V', 'B']
Ncols = len(colors)
colors_set = set(range(1,Ncols+1))

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

print('Number of tests =', compt)
start = fun_time(start)
print()

##
print('All solutions...')

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
                neighbors = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords_all]
                for a,b in neighbors:
                    if cult not in impossibilities[a][b]:
                        impossibilities[a][b].append(cult)

        region = list_regions[ind]
        list_cult_region = rec_mini([], [], cultures_types[len(region)-1], region, [], 0, impossibilities)
        for cult_region in list_cult_region:
            list_solutions = rec_maxi(solution, impossibilities, list_solutions, cult_region, list_regions, ind+1)

    return list_solutions

cultures_types = [[i+1 for i in range(size)] for size in range(1,size_max_reg+1)]
solution0 = []
impossibilities0 = [[[] for j in jz] for i in iz]
list_solutions0 = []
cult_region = []
list_regions = sorted_regs
# list_regions = [[[0, 0], [0, 1], [1,0]], [[0,2], [0,3], [1, 2]]]
ind = 0

list_solutions = rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind)
# print(list_solutions)
Nsol = len(list_solutions)
print('Number of solutions =', Nsol)
start = fun_time(start)
print()

##
print('Uniqueness...')

array_solutions = np.full((Nsol, Ni, Nj), 0)
for ind_sol in range(Nsol):
    for ind_reg, reg in enumerate(sorted_regs):
        for ind_ter, ter in enumerate(reg):
            array_solutions[ind_sol, ter[0], ter[1]] = list_solutions[ind_sol][ind_reg][ind_ter]

#
# unique = np.full((Ni,Nj), True)
# for ind_sol in range(Nsol):
#     unique *= (array_solutions[ind_sol,:,:] == list_cultures)
#
# print(unique*1)
#

# list_unique = []
bol0 = True
inds = set(range(Nsol))
unique = np.full((Ni,Nj), 0)
while bol0:

    nbs = np.full((Ni,Nj), 0)
    for ind_sol in inds:
        nbs += (array_solutions[ind_sol,:,:] == list_cultures)

    i,j = np.unravel_index(np.argmin(nbs), nbs.shape)
    # list_unique.append([i,j])
    unique[i,j] = list_cultures[i,j]
    # print(nbs)

    inds = set([ind for ind in inds if array_solutions[ind,i,j]==list_cultures[i,j]])
    bol0 = (len(inds) > 1)
    print([i,j], len(inds))

start = fun_time(start)

##
arr_cols_reduced = 1.*arr_cols
for i in iz:
    for j in jz:
        if not unique[i,j]:
            arr_cols_reduced[i,j] = np.nan

##
#
# tmp = [[i,j] for i in iz for j in jz if unique[i,j]]
# for i,j in tmp:
#     print(list_cultures[i,j], a[i,j])
#
# #
# for ind_sol in range(Nsol):
#     if (array_solutions[ind_sol,:,:]==list_cultures).all():
#         print(ind_sol)

    ##

bol_plot = 0
if bol_plot:
    plt.close('all')

    minor_y = np.arange(0.5, Ni-1)
    minor_x = np.arange(0.5, Nj-1)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    cmap = ListedColormap(colors)
    ax.imshow(arr_cols_reduced, cmap = cmap)
    ax.set_xticks(minor_x, [])#, minor=True)
    ax.set_yticks(minor_y, [])#, minor = True)
    ax.grid(True)#, which='minor')#, color='k', alpha=0.2)
    for i in iz:
        for j in jz:
            if unique[i][j]:
                text = ax.text(j, i, unique[i][j],ha="center", va="center", color="k", fontsize=20)

    if 0:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(arr_cols, cmap = cmap)
        ax.set_xticks(minor_x, [])#, minor=True)
        ax.set_yticks(minor_y, [])#, minor = True)
        ax.grid(True)#, which='minor')#, color='k', alpha=0.2)
        for i in iz:
            for j in jz:
                # unique  list_cultures  board_solutions  solution
                text = ax.text(j, i, list_cultures[i][j],ha="center", va="center", color="k", fontsize=20)

    plt.show()

##

df = pd.DataFrame(unique)
df[df == 0] = ''
for i in iz:
    for j in jz:
        if unique[i,j]:
            df[j][i] = colors_small[arr_cols[i,j]-1] + ' ' +  str(df[j][i])

while 1:
    print(tabulate(df.values, tablefmt='grid'))
    print()
    print('Which type ?')
    print('  0 = Color')
    print('  1 = Number')
    typ = int(input())
    print()

    print('Where ?')
    i = int(input('i = '))
    j = int(input('j = '))
    print()
    col = colors_small[arr_cols[i,j]-1]
    num = list_cultures[i,j]
    if typ == 0:
        df[j][i] = col
        print(df[j][i])
    elif typ == 1:
        df[j][i] = col + ' ' +  str(num)
        print(df[j][i])


## OLD Resolution

# solution = np.full((Ni,Nj),0)
# sets = [set(range(i+1, size_max_reg+1)) for i in range(size_max_reg+1)]
# impossibilities = [[set() for j in jz] for i in iz]
# for reg in list_regs:
#     leni = len(reg)
#     for i,j in reg:
#         impossibilities[i][j] = sets[leni]
# seti = sets[0]
# poss = [len(reg)*[reg] for reg in list_regs]
# remaining_cults = copy.deepcopy(coords_all)
# #
# bol_changed = True
# while remaining_cults and bol_changed:
#
#     for ind_max, ter in enumerate(remaining_cults):
#         i,j = ter
#         # Solution because only one possibility in one terrain
#         if len(impossibilities[i][j]) == size_max_reg-1:
#             print('Terrain')
#             for missing_crop in seti-impossibilities[i][j]:
#                 del remaining_cults[ind_max]
#             break
#     else:
#         poss_tmp = [[poss[x][y], y+1] for x in range(len(poss)) for y in range(len(poss[x]))]
#         for test in poss_tmp:
#             # Solution because only one possibility for one culture
#             if len(test[0]) == 1:
#                 print('Culture')
#                 i,j = test[0][0]
#                 missing_crop = test[1]
#                 remaining_cults.remove([i,j])
#                 break
#         else:
#             bol_changed = False
#             # print('new')
#             for ind_reg in range(len(poss)):
#                 for crop in range(len(poss[ind_reg])):
#                     neigh_inter = [ter for ter in coords_all if ter not in list_regs[ind_reg]]
#                     # input(poss[ind_reg][crop])
#                     for i,j in poss[ind_reg][crop]:
#                         alls = [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]]
#                         neigh_inter = [ter for ter in alls if ter in neigh_inter]
#                         # print(neigh_inter)
#                         if not neigh_inter:
#                             break
#                     else:
#                         print('Imposs')
#                         print(neigh_inter, crop+1)
#                         # input()
#                         for i,j in neigh_inter:
#                             if not (crop+1) in impossibilities[i][j]:
#                                 bol_changed = True
#                                 impossibilities[i][j].add(crop+1)
#             continue
#
#     # MAJ
#     print(i,j)
#     print(missing_crop)
#     solution[i,j] = missing_crop
#     if [i,j] in poss[board[i,j]-1][missing_crop-1]:
#         poss[board[i,j]-1][missing_crop-1].remove([i,j])
#     for a,b in [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]]:
#         if [a,b] in remaining_cults:
#             impossibilities[a][b].add(missing_crop)
#             if [a,b] in poss[board[a,b]-1][missing_crop-1]:
#                 poss[board[a,b]-1][missing_crop-1].remove([a,b])
#     # print(impossibilities)
#     # print(poss)
#     # input()