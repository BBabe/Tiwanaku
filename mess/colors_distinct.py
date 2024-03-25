'''

'''
import json
import glob as glob
import os
from random import randrange
import numpy as np
import matplotlib.pyplot as plt
# local
from find_forms_cultures_functions import fun_date, fun_permut, fun_init, fun_recursion, fun_first_couples,fun_time

## Input parameters

# Number of lines
Ni = 4
# Number of columns
Nj = 5
# Maximal region size
size_max_reg = 4

# Load already existing file
bool_load = 1

# Name of output file in output folder
folder_out = 'test_data'
str_today = fun_date()
file_out = '{}_{}_{}_{}.json'.format(Ni, Nj, size_max_reg, str_today)

## Small computations and loading

iz = range(Ni)
jz = range(Nj)
# All terrains coordinates
coords_all = [[i, j] for i in iz for j in jz]

## Load

list_paths = glob.glob(os.path.join(folder_out, file_out[:5] + '*'))
if list_paths:
    path = list_paths[0]
    with open(path, "r") as fp:
        list_results = json.load(fp)

## Computations

# ind = randrange(len(list_results))
list_regions, list_cultures = list_results[ind]

board = np.full((Ni, Nj), 0)
for ind, region in enumerate(list_regions):
    for i,j in region:
        board[i,j] = ind

## matrix_neighbors

for region in list_regions:
    print(region)

Nreg = len(list_regions)
matrix_neighbors = np.full((Nreg, Nreg), 0)
for ind_reg, region in enumerate(list_regions):
    for i,j in region:
        neighbors = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords_all]
        for a,b in neighbors:
            ind2 = board[a,b]
            matrix_neighbors[ind_reg, ind2] = 1
            matrix_neighbors[ind2, ind_reg] = 1
for i in range(Nreg):
    matrix_neighbors[i,i] = 0

print(matrix_neighbors)

##



## Plots

if 1:
    plt.close('all')

    minor_y = np.arange(0.5, Ni-1)
    minor_x = np.arange(0.5, Nj-1)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # colors = ['brown', 'yellow', 'green', 'blue']
    # cmap = ListedColormap(colors)
    ax.imshow(board, cmap = 'tab20c')


    # ax.set_yticks(jz, jz[::-1])
    ax.set_xticks(minor_x, [])#, minor=True)
    ax.set_yticks(minor_y, [])#, minor = True)
    ax.grid(True)#, which='minor')#, color='k', alpha=0.2)
    # ax.grid()

    for i in iz:
        for j in jz:
            text = ax.text(j, i, list_cultures[i][j],ha="center", va="center", color="k", fontsize=40)


    plt.show()

