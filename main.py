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
# import warnings
# warnings.filterwarnings("ignore")

# local modules
from functions import put_numbers, put_regions, put_colors, rec_maxi, init_rec, init_board, fun_update_small, fun_neighbors, fun_time, fun_permut
## Input parameters

# Smartphone app can reset and lose progress --> save progress (bol = bool...)
# and load it if necessary
bol_save = 1 # No need when on computer
# bol_save = int(input('Generate new game (1) or load previous one (0)? '))

# Number of columns = 5 (easy) or 9 (difficult)
Nj = 5
# Number of lines
Ni = 5
# Maximal region size
size_max_reg = 5

##

# List of possible cultures
cults = range(1, size_max_reg+1)
# Set of possible cultures
set_max = set(cults)
# Se
sets = [set_max - set([ind]) for ind in cults]

NN = Ni*Nj
iz = range(Ni)
jz = range(Nj)
# All terrains coordinates
coords_all = [[i, j] for i in iz for j in jz]

sep = ";"

colors = ['peru', 'gold', 'limegreen', 'steelblue']
colors_small = ['M', 'J', 'V', 'B']
Ncols = len(colors)
colors_set = set(range(1,Ncols+1))

path_df = '0df.npy'
path_df0 = '0df0.npy'

path_tetris = 'data/tetris_forms.json'

##
##################################
##

if bol_save:
    ##################################
    print('Generation of cultures...')
    start = time.time()

    compteur, Ns, list_cultures, list_per_cults, impossibilities = put_numbers([Ni, Nj, NN, size_max_reg, coords_all])

    print('Number of tests =', compteur)
    start = fun_time(start)
    print()

    ##################################
    print('Associated regions...')

    global_var = path_tetris, NN, Ni, Nj, coords_all
    compt, sorted_regs, board = put_regions(global_var, Ns, list_per_cults, list_cultures)

    print('Number of tests =', compt)
    start = fun_time(start)
    print()

    ##################################
    print('Possible colors set...')

    global_var = Ni, Nj, Ncols, colors_set, coords_all
    arr_cols = put_colors(global_var, sorted_regs, board)

    print()

    ##################################
    print('All solutions...')

    permuts = fun_permut(size_max_reg)
    global_var = size_max_reg, iz, jz, coords_all
    solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind = init_rec(global_var, sorted_regs, board)
    list_solutions = rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind, [permuts, coords_all])

    print('Number of solutions =', len(list_solutions))
    start = fun_time(start)
    print()

    ##################################
    print('Initialize board...')

    global_var = Ni, Nj, iz, jz, path_df0, path_df, colors_small
    df0, df = init_board(global_var, sorted_regs, list_solutions, list_cultures, arr_cols)

    print()
    print()

    ##
    ##################################
    ##


else:
    np_tmp = np.load(path_df0, allow_pickle=True)
    df0 = pd.DataFrame(np_tmp)
    np_tmp = np.load(path_df, allow_pickle=True)
    df = pd.DataFrame(np_tmp)


##################################

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
