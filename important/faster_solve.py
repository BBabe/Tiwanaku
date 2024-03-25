import numpy as np
import copy
from operator import itemgetter
##

Ni = 5
Nj = 5
size_max_reg = 5
cults = range(1, size_max_reg+1)

iz = range(Ni)
jz = range(Nj)
coords_all = [[i, j] for i in iz for j in jz]

##

ind = 1
if ind:
    list_cultures = np.array([[1, 2, 1, 3, 2],
        [4, 3, 4, 5, 1],
        [1, 2, 1, 2, 4],
        [3, 5, 4, 5, 3],
        [1, 2, 3, 1, 2]])
    board = np.array([[2, 2, 5, 5, 4],
        [7, 7, 5, 5, 4],
        [7, 7, 1, 5, 4],
        [3, 7, 6, 6, 4],
       [3, 3, 6, 6, 6]])
    sorted_regs = [[[2, 2]], [[0, 1], [0, 0]], [[3, 0], [4, 0], [4, 1]], [[2, 4], [1, 4], [3, 4], [0, 4]], [[1, 3], [1, 2], [2, 3], [0, 2], [0, 3]], [[3, 3], [4, 3], [3, 2], [4, 2], [4, 4]], [[3, 1], [2, 1], [2, 0], [1, 0], [1, 1]]]
else:
    list_cultures = np.array([[1, 4, 1, 3, 1],
        [2, 3, 2, 4, 2],
        [1, 5, 1, 5, 1],
        [3, 4, 2, 4, 3],
        [2, 1, 3, 1, 2]])
    board = np.array([[8, 8, 1, 7, 2],
        [3, 8, 8, 7, 7],
        [3, 8, 5, 7, 7],
        [6, 6, 5, 5, 4],
        [6, 6, 5, 4, 4]])
    sorted_regs = [[[0, 2]], [[0, 4]], [[1, 0], [2, 0]], [[3, 4], [4, 4], [4, 3]], [[3, 3], [3, 2], [2, 2], [4, 2]], [[3, 1], [3, 0], [4, 1], [4, 0]], [[2, 3], [1, 3], [0, 3], [1, 4], [2, 4]], [[2, 1], [1, 1], [1, 2], [0, 1], [0, 0]]]

##

neighbors_all = [[[] for j in jz] for i in iz]
for i in iz:
    for j in jz:
        reg = sorted_regs[board[i,j]-1]
        coords = [ter for ter in coords_all if ter not in reg]
        neighbors_all[i][j] = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords]

##

impos = [[set() for j in jz] for i in iz]
# list_sets = [set(range(size,size_max_reg+1)) for size in range(2,size_max_reg+2)]
for i in iz:
    for j in jz:
        leni = len(sorted_regs[board[i,j]-1])
        # impos[i][j] = list_sets[leni-1]
        impos[i][j] = set(range(leni+1,size_max_reg+1))

impos0 = copy.deepcopy(impos)

##


''' Tant qu'il y a des régions qui ont subi des modifications... '''
# ind_reg = 0
set_max = set(cults)
list_modif = list(range(len(sorted_regs)))
while list_modif:
    ind_reg = list_modif[0]
    set0 = set(list_modif)
    set0.remove(ind_reg)
    reg = sorted_regs[ind_reg]
    print(ind_reg+1)
    # print(reg)

    ''' Pour la région courante, liste des voisins à modifier pour chaque culture '''
    # coords = [ter for ter in coords_all if ter not in reg]
    neigh_cult = [[] for _ in cults]
    bool_cult = size_max_reg*[0]
    for i,j in reg:
        # print('ter =', i,j)
        # neighbors = [[a,b] for a in [i-1,i,i+1] for b in [j-1,j,j+1] if [a,b] in coords]
        neighbors = neighbors_all[i][j]
        for cult in cults:
            if cult not in impos[i][j]:
                if bool_cult[cult-1]:
                    neigh_cult[cult-1] = [ter for ter in neighbors if ter in neigh_cult[cult-1]]
                else:
                    neigh_cult[cult-1] = neighbors#.copy()
                    bool_cult[cult-1] = 1
    #             print(cult, neigh_cult[cult-1])
    # print(neigh_cult)
    # print()

    ''' Modification de ces voisins '''
    set_tmp = set()
    for ind_cult, list_news in enumerate(neigh_cult):
        for i,j in list_news:
            cult = ind_cult+1
            if cult not in impos[i][j]:
                # print(i,j, '    ', cult)
                ind_reg = board[i,j]-1
                set_tmp.add(ind_reg)
                impos[i][j].add(cult)


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
                seti = set_max.copy()
                seti.remove(cult)
                impos[i][j] = seti

    # for i in iz:
    #     print(impos[i])


    list_modif = list(set_tmp | set0)
    # list_modif = list(set_tmp)
    # input('next ?')
    # print()
    # if ind_reg == 6:
    #     input()


##

for i in iz:
    print(impos0[i])


print()
for i in iz:
    print(impos[i])

##

result = np.full((Ni,Nj),0)
for i in iz:
    for j in jz:
        if len(impos[i][j]) == 4:
            result[i,j] = list(set_max - impos[i][j])[0]
print(result)