from random import randrange, choice#, shuffle
import numpy as np
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
    impos_tmp = [ter for ter in neighbors if ter in coords_all] # neighbors which are on the board
    for a,b in impos_tmp: # i,j could be re-used
        impossibilities[a,b] = cult
    return impossibilities

def fun_neighbors(i,j):
    ''' Coordinates of all 8 neighbors of terrain [i,j] '''
    return [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]] # list also contains ter, which is not a problem

##

Ns = np.zeros((size_max_reg,))

bol = False
compteur = 0
while not bol:
    compteur += 1
    # print(compteur)
    bol = True
    Nmin = 1
    Nmax = Nj
    board = np.zeros((Ni,Nj))
    impossibilities = np.zeros((Ni, Nj))
    for crop in range(size_max_reg, 1, -1):
        N = randrange(Nmin, Nmax+1)

        ind = 0
        while ind < N:
            possib = [[i,j] for i,j in coords_all if not impossibilities[i,j]]
            if possib:
                a,b = choice(possib)
                board[a,b] = crop
                impossibilities = fun_update_small(a,b, crop, impossibilities, coords_all)
                ind += 1
            else:
                break
        if ind < Nmin:
            bol = False
            break

        Ns[crop-1] = ind
        Nmin = ind
        Nsofar = Ns[-1]*size_max_reg + sum([(Ns[size-1]-Ns[size])*size for size in range(crop, size_max_reg)])
        Nmax = int(ind + (NN - Nsofar)/(crop-1))

        impossibilities = 1.*board

    ##

    if bol:
        crop = 1
        for a,b in [[i,j] for i,j in coords_all if not board[i,j]]:
            if impossibilities[a,b]:
                bol = False
                break
            board[a,b] = crop
            impossibilities = fun_update_small(a,b, crop, impossibilities, coords_all)


    ##

    # input(board)
print(compteur)
print(board)

Ns[0] = NN - sum(Ns)
print(Ns)

