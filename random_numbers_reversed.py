import time
start = time.time()
from random import randrange, choice, shuffle
import numpy as np
import json
import matplotlib.pyplot as plt
## Input parameters

# Number of lines
Ni = 5
# Number of columns
Nj = 9
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

##

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

    ##

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


    ##

    # input(list_cultures)
print(compteur)
print(list_cultures)

Ns[-1] = NN - sum(Ns)
print([Ns[i]-Ns[i+1] for i in range(len(Ns)-1)] + [Ns[-1]])

##

# All possible region forms
with open('data/tetris_forms.json', "r") as fp:
    tetris_forms = json.load(fp)

##

compt = 0
bol_filled = True
while bol_filled:
    compt += 1
    poss = np.ones((Ni,Nj))
    board = np.full((Ni,Nj),0)

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

        for a,b in reg:
            board[a,b] = ind_reg
            poss[a,b] = 0

        for a,b in coords_all:
            if poss[a,b]:
                ind_reg += 1
                break
        else:
            bol_filled = False


print(compt)

print(time.time() - start)

##

plt.close('all')

minor_y = np.arange(0.5, Ni-1)
minor_x = np.arange(0.5, Nj-1)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax.imshow(board, cmap = 'tab20')
# ax.imshow(list_cultures, cmap = 'tab10')

ax.set_xticks(minor_x, [])#, minor=True)
ax.set_yticks(minor_y, [])#, minor = True)
ax.grid(True)#, which='minor')#, color='k', alpha=0.2)

for i in iz:
    for j in jz:
        text = ax.text(j, i, list_cultures[i][j],ha="center", va="center", color="k", fontsize=20)

plt.show()
