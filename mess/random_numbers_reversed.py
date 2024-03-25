import time
from random import randrange, choice, shuffle
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
## Input parameters

# Number of lines
Ni = 5
# Number of columns
Nj = 7
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
    impossibilities = np.zeros((Ni, Nj))
    for crop in range(1, size_max_reg):
        N = randrange(Nmin, Nmax+1)

        ind = 0
        while ind < N:
            possib = [[i,j] for i,j in coords_all if not impossibilities[i,j]]
            if possib:
                a,b = choice(possib)
                list_cultures[a,b] = crop
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
                impossibilities = fun_update_small(a,b, crop, impossibilities, coords_all)
        else:
            bol = False


    #

    # input(list_cultures)
print('Number of tests =', compteur)
# print(list_cultures)

Ns[-1] = NN - sum(Ns)
print('Number of regions of size', list(range(1, size_max_reg+1)), '=', [Ns[i]-Ns[i+1] for i in range(len(Ns)-1)] + [Ns[-1]])

start = fun_time(start)
print()

##

# All possible region forms
with open('data/tetris_forms.json', "r") as fp:
    tetris_forms = json.load(fp)

##

print('Associated regions...')
compt = 0
bol_filled = True
while bol_filled:
    compt += 1
    poss = np.ones((Ni,Nj))
    board = np.full((Ni,Nj),0)
    list_regs = []

    bol_filled = True
    ind_reg = 1
    while bol_filled:

        i,j = np.unravel_index(np.argmax(list_cultures*poss), list_cultures.shape)
        size = list_cultures[i,j]
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

        for a,b in coords_all:
            if poss[a,b]:
                ind_reg += 1
                break
        else:
            bol_filled = False


print('Number of tests =', compt)
start = fun_time(start)
print()

##

print('Possible colors set...')
# colors = ['brown', 'yellow', 'green', 'blue']
colors = ['peru', 'gold', 'limegreen', 'steelblue']
Ncols = len(colors)
colors_set = set(range(1,Ncols+1))

Nreg = len(list_regs)

bol_no = True
compt = 0
while bol_no:
    compt += 1

    impossibilities = [set() for _ in range(Nreg)]
    arr_cols = np.full((Ni,Nj),0)
    cols_used = set()
    for _ in list_regs:

        # for nocols in impossibilities:
            # print(nocols)
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
            # input(ind_worst_reg)
            # print()
            reg = list_regs[ind_worst_reg]
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
    # input(arr_cols)
    # print()



print('Number of tests =', compt)
start = fun_time(start)


##

# plt.close('all')

minor_y = np.arange(0.5, Ni-1)
minor_x = np.arange(0.5, Nj-1)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

cmap = ListedColormap(colors)
ax.imshow(arr_cols, cmap = cmap)
# ax.imshow(list_cultures, cmap = 'tab10')

ax.set_xticks(minor_x, [])#, minor=True)
ax.set_yticks(minor_y, [])#, minor = True)
ax.grid(True)#, which='minor')#, color='k', alpha=0.2)

for i in iz:
    for j in jz:
        text = ax.text(j, i, list_cultures[i][j],ha="center", va="center", color="k", fontsize=20)

plt.show()
