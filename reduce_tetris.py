import json
import os
import copy
## Parameters

size_max = 5
folder = '/home/chilly-ben/Documents/Créations/Code/Tiwanaku/data'
name = 'tetris_forms.json'
path = os.path.join(folder, name)

## Functions

with open(path, "r") as fp:
    tetris_forms = json.load(fp)
##

print(len(tetris_forms[-1]))
forms_max = copy.deepcopy(tetris_forms[-1])
for form in forms_max:

    l_ter = []
    l_nb = []
    for i,j in form:
        alls = [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]]
        neighs = [ter for ter in alls if ter not in form]
        for ter in neighs:
            if ter not in l_ter:
                l_ter.append(ter)
                l_nb.append(1)
            else:
                ind = l_ter.index(ter)
                l_nb[ind] += 1

    if max(l_nb) == size_max:
        print(form)
        tetris_forms[-1].remove(form)

print(len(tetris_forms[-1]))
##

# with open(path, "w") as fp:
#     json.dump(tetris_forms, fp)
