'''
Start computations by filling boards with numbers (= cultures = crops),
following the only rule of two same crops cannot be next to one another.
Regions will be fitted into this filled board only after (with high probability).
This appears to be way much faster than my original method, which consisted in
iteratively filling the board with filled regions compatible with existing board
(see important/old_all_solutions_functions.py)
'''
print('Loading modules...')
import time
import numpy as np
import pandas as pd
import os
import json
# import warnings
# warnings.filterwarnings("ignore")

# local modules
from functions import put_numbers, put_regions, put_colors, rec_maxi, init_rec, init_board, interaction, fun_plot, fun_time, fun_permut, fun_neighbors_all
## Input parameters
# 0 = plot whole solution; 1 = interact with user throughout the game
bol_interaction = 0

# Smartphone app can reset and lose progress --> save progress and load it if necessary
bol_save = 1 # No need when on computer
# bol_save = int(input('Generate new game (1) or load previous one (0)? '))

# Number of columns = 5 (easy) or 9 (difficult)
Nj = 5

# Paths of data: board in progress and tetris forms
folder_data = 'data'
path_df = os.path.join(folder_data,'board_in_progress.npy')
path_df0 = os.path.join(folder_data,'board_complete.npy')
path_tetris = os.path.join(folder_data,'tetris_forms.json')

## Other parameters

# Number of lines
Ni = 5
NN = Ni*Nj
# Coordinates
iz = range(Ni)
jz = range(Nj)
coords_all = [[i, j] for i in iz for j in jz]

# Maximal region size = Maximum culture number
size_max_reg = 5

# Colors corresponding to the game
colors = ['peru', 'gold', 'limegreen', 'steelblue']
colors_small = ['M', 'J', 'V', 'B']
Ncols = len(colors)
colors_set = set(range(1,Ncols+1))

# All possible region forms (some 5 regions are impossible in this game, when U or L form)
with open(path_tetris, "r") as fp:
    tetris_forms = json.load(fp)

global_var = Ni, Nj, path_df, path_df0, NN, iz, jz, coords_all, size_max_reg, colors, colors_small, Ncols, colors_set

##
print('Small computations...')

# All possible sequences of cultures, for all region sizes
permuts = fun_permut(size_max_reg)
# All tetris forms for each territory i,j and size
regs_ij = fun_neighbors_all(global_var, tetris_forms)

##################################
##################################
##################################
print()
if bol_save:
    start = time.time()
    bol_impos = True
    # Some boards filled with cultures allow no associated regions
    while bol_impos:
        ##################################
        print('Generation of cultures...')

        compteur, Ns, list_cultures, list_per_cults, impossibilities = put_numbers(global_var)

        print('Number of tests =', compteur)
        start = fun_time(start)
        print()

        ##################################
        print('Associated regions...')

        compt, sorted_regs, board, bol_impos = put_regions(global_var, Ns, list_per_cults, list_cultures, regs_ij)

        print('Number of tests =', compt)
        start = fun_time(start)
        print()

    ##################################
    print('Possible colors set...')

    arr_cols = put_colors(global_var, sorted_regs, board)

    print()

    ##################################
    print('All solutions corresponding to these regions...')

    solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind = init_rec(global_var, sorted_regs, board)
    list_solutions = rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind, permuts, coords_all)

    Nsol = len(list_solutions)
    print('Number of solutions =', Nsol)
    start = fun_time(start)
    print()

    ##################################
    print('Initialize board with unique solution...')

    df0, df = init_board(global_var, sorted_regs, list_solutions, Nsol, list_cultures, arr_cols)

    print()
    print()

    ##################################
    ##################################
    ##################################

# Load
else:
    np_tmp = np.load(path_df0, allow_pickle=True)
    df0 = pd.DataFrame(np_tmp)
    np_tmp = np.load(path_df, allow_pickle=True)
    df = pd.DataFrame(np_tmp)


##################################

# Accompany user throughout the game
if bol_interaction:

    interaction(global_var, df0, df)

# Plot whole solution chosen by user
else:

    fun_plot(global_var, list_solutions, Nsol, arr_cols, sorted_regs)
