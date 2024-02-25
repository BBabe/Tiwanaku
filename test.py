'''

'''
import numpy as np
from random import randrange, choice
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import ListedColormap
import copy
##

Ni = 5
Nj = 5

# Nter = 4
Ncul = 5

iz = range(Ni)
jz = range(Nj)
# terz = range(Nter)
# culz = range(Ncul)

coords0 = [[i, j] for i in iz for j in jz]

##

def fun_neighbors(ter):
    i, j = ter
    return [[i, j-1], [i, j+1], [i-1, j], [i+1, j]]

##

remaining_coords = coords0.copy()
list_regions = []
for i in iz:
    for j in jz:
        ter = [i,j]
        if ter in remaining_coords:
            size_max = min(Ncul, len(remaining_coords))
            '''
            size_reg = randrange(size_max) + 1
            '''
            size_reg = randrange(size_max) + 1
            # size_reg = randrange(1, size_max) + 1

            region = []
            possible_coords = []
            while len(region) < size_reg:
                region.append(ter)
                remaining_coords.remove(ter)

                neighbors_all = fun_neighbors(ter)
                neighbors = [neighbor for neighbor in neighbors_all if neighbor in remaining_coords]
                possible_coords.extend(neighbors)
                if possible_coords:
                    ter = choice(possible_coords)
                    # print(possible_coords)
                    possible_coords.remove(ter)
                    # print(ter)
                else:
                    break
            list_regions.append(region)
list_sorted0 = sorted(list_regions, key = len)
list_unsorted0 = list_sorted0.copy()
list_unsorted0.reverse()
# list_unsorted0 = sorted(list_regions, key = len, reverse=True)

##

board = np.full((Ni, Nj), 0)
for ind, region in enumerate(list_unsorted0):
    for i,j in region:
        board[i,j] = ind

##

for region in list_unsorted0:
    print(region)
##

Nreg = len(list_unsorted0)
matrix_neighbors = np.full((Nreg, Nreg), 0)
for ind_reg, region in enumerate(list_unsorted0):
    for i,j in region:
        neighbors = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords0]
        # neighbors = [neighbor for neighbor in neighbors_all if neighbor in coords0]
        for a,b in neighbors:
            ind2 = board[a,b]
            matrix_neighbors[ind_reg, ind2] = 1
            matrix_neighbors[ind2, ind_reg] = 1
for i in range(Nreg):
    matrix_neighbors[i,i] = 0

##

colors = ['brown', 'yellow', 'green', 'blue']
remaining_colors = colors.copy()
list_cols = np.zeros((Nreg,), dtype='<U25')
ind_reg1 = 0
list_unsorted = list_unsorted0.copy()
while list_unsorted:
    region = list_unsorted.pop(0)

    if len(list_unsorted)+1 > len(remaining_colors):
        possible_colors = colors.copy()
        for ind_reg2, bol_nei in enumerate(matrix_neighbors[ind_reg1,:]):
            if bol_nei:
                col2 = list_cols[ind_reg2]
                if col2 in possible_colors:
                    possible_colors.remove(col2)
        color = choice(possible_colors)

    else:
        color = choice(remaining_colors)
    list_cols[ind_reg1] = color
    if color in remaining_colors:
        remaining_colors.remove(color)

    ind_reg1 += 1

##
board_cols = np.zeros((Ni, Nj))#, dtype='<U25')
for ind, region in enumerate(list_unsorted0):
    for i,j in region:
        # board_cols[i,j] = list_cols[ind]
        col = list_cols[ind]
        board_cols[i,j] = colors.index(col)

##


# list_region = []
# culture = []
# region =[[0, 0], [0, 1], [1,0]]
# cul_remaining = cultures_types[len(region)-1]
# list_lists = []
# ind = 0
# impossibilities = [[[] for i in iz] for j in jz]


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


# list_lists = rec_mini(list_region, culture, cul_remaining, region, list_lists, ind, impossibilities)
# print(list_lists)

##


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
impossibilities0 = [[[] for i in iz] for j in jz]
list_solutions0 = []
cult_region = []
list_regions = list_sorted0
# list_regions = [[[0, 0], [0, 1], [1,0]], [[0,2], [0,3], [1, 2]]]
ind = 0

list_solutions = rec_maxi(solution0, impossibilities0, list_solutions0, cult_region, list_regions, ind)
print(list_solutions)

##


# cultures_types = [[i+1 for i in range(size)] for size in range(1,6)]
# list_boards = []
# board_cultures = np.zeros((Ni, Nj))
# # possibilities = np.zeros((Ni, Nj))
# possibilities = [[cultures_types[-1] for i in iz] for j in jz]
# for region in list_sorted0:
#     size = len(region)
#     cultures = cultures_types[size-1]
#     for ter in region:
#
#
#     while cultures:
#         culture = choice(cultures)


##

plt.close('all')

minor_y = np.arange(0.5, Ni-1)
minor_x = np.arange(0.5, Nj-1)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

cmap = ListedColormap(colors)
ax.imshow(board_cols, cmap = cmap)
# ax.imshow(board_cols, cmap = 'tab20c')


# ax.set_yticks(jz, jz[::-1])
ax.set_xticks(minor_x, minor=True)
ax.set_yticks(minor_y, minor = True)
ax.grid(which='minor')#, color='k', alpha=0.2)

plt.show()

##

