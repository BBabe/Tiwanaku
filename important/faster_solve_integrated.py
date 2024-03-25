import numpy as np
import copy
from operator import itemgetter
from random import shuffle, choice
##

Ni = 5
Nj = 5
size_max_reg = 5
cults = range(1, size_max_reg+1)
set_max = set(cults)
sets = [set_max - set([ind]) for ind in cults]

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
# for i in iz:
#     print(impos0[i])
# print()

##

def fun_copy(changing_lists):
    copy_list = []
    for var in changing_lists:
        copy_list.append(copy.deepcopy(var))
    return copy_list

##


def fill_impos(impos, sorted_regs, board, list_modif):
# if 1:
    ''' Tant qu'il y a des régions qui ont subi des modifications... '''
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
                    if len(impos[i][j]) == size_max_reg-1 and impos[i][j] != sets[cult-1]:
                        return True, impos
                    else:
                        impos[i][j] = sets[cult-1]
                    # if len(impos[i][j]) == size_max_reg:
                    #     return True, impos
                elif len(ters) == 0:
                    return True, impos

        list_modif = list(set_tmp | set0)
    return False, impos

##


def maj_when_4(ind_reg, impos):
    ''' Actualiser régions modifiées si impos rempli dans une case '''
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
    return False, impos


def fun_rec(changing_lists, remainings0, ter, cult):
    # Preserve to-be-modified lists for other recursions
    list_impos, impos = fun_copy(changing_lists)

    #print(ter, cult)
    #print('impos')
    #print(impos)
    #print()

    # Update lists with current culture
    list_modif = list(range(len(sorted_regs)))
    if ter:
        i,j = ter
        impos[i][j] = sets[cult-1]
        ind_reg = board[i,j]-1
        list_modif = [ind_reg]
        bol5, impos = maj_when_4(ind_reg, impos)
        if bol5:
            #print('END')
            return list_impos


        # other_ters = [ter for ter in sorted_regs[ind_reg] if ter!=[i,j]]
        # for a,b in other_ters:
        #     impos[a][b].add(cult)
        #     if len(impos[a][b]) == size_max_reg:
        #         #print('END')
        #         return list_impos
        # #     elif len(impos[a][b]) == size_max_reg-1:

        #print(impos)
        #print()

    bol5, impos = fill_impos(impos, sorted_regs, board, list_modif)
    if bol5:
        #print('END')
        return list_impos

    else:
        #print(impos)
        #print()
        remainings = copy.deepcopy(remainings0)
        #print('remainings')
        #print(remainings)
        #print()
        for i,j in remainings0:
            if len(impos[i][j]) == size_max_reg-1:
                remainings.remove([i,j])
        #print(remainings)
        #print()

        # End of recursion
        if not remainings:
            if impos in list_impos:
                input('Already')
            else:
                bol_tmp = False
                for reg in sorted_regs:
                    l = []
                    for i,j in reg:
                        c = list(set_max - impos[i][j])[0]
                        if c in l:
                            bol_tmp = True
                            break
                        else:
                            l.append(c)
                    if bol_tmp:
                        break
                if bol_tmp:
                    input('redondance')

                for i,j in coords_all:
                    tmp = [list(set_max - impos[a][b])[0] for a in [i,i+1] for b in [j,j+1] if [a,b] in coords_all]
                    l = np.zeros((size_max_reg,))
                    for c in tmp:
                        l[c-1]+=1
                    if max(l) > 1:
                        input('règle')
                        break


                list_impos.append(impos)
                print(len(list_impos))
            #print('solution')
            # result = np.full((Ni,Nj),0)
            # for i in iz:
            #     for j in jz:
            #         result[i,j] = list(set_max - impos[i][j])[0]
            # input(result)
            #print()
            #print()
            # input()

        # Recursion
        else:
            i,j = choice(remainings)
            remainings.remove([i,j])
            cults_rem = set_max - impos[i][j]
            for cult in cults_rem:
                list_impos = fun_rec([list_impos, impos], remainings, [i,j], cult)

        return list_impos

##


list_impos = fun_rec([[], impos0], coords_all, [], 0)
print(len(list_impos))

# for impos in list_impos:
    # result = np.full((Ni,Nj),0)
    # for i in iz:
    #     for j in jz:
    #         result[i,j] = list(set_max - impos[i][j])[0]
    # print(result)
#     print()

##

# for impos in list_impos0:
#     if impos not in list_impos:
#         result = np.full((Ni,Nj),0)
#         for i in iz:
#             for j in jz:
#                 result[i,j] = list(set_max - impos[i][j])[0]
#         input(result)

##

# coords_shuffle = copy.deepcopy(coords_all)
while 0:
    bol5, impos = fill_impos(impos, sorted_regs, board)
    for i in iz:
        print(impos[i])

    shuffle(coords_shuffle)
    for i,j in coords_shuffle:
        tmp = list(set_max - impos[i][j])
        if len(tmp) > 1:
            cult = choice(tmp)
            break
    else:
        break
    print()
    print(i,j, '    ', cult)
    impos[i][j] = sets[cult-1]

    for a,b in sorted_regs[board[i,j]-1]:
        impos[a][b].add(cult)
    impos[i][j].remove(cult)
    print()
    for i in iz:
        print(impos[i])
    input()


##

# bol5, impos = fill_impos(impos, sorted_regs, board)

# for i in iz:
#     print(impos0[i])

# print()
# for i in iz:
#     print(impos[i])
#
# #
#
# result = np.full((Ni,Nj),0)
# for i in iz:
#     for j in jz:
#         if len(impos[i][j]) == 4:
#             result[i,j] = list(set_max - impos[i][j])[0]
# print(result)
