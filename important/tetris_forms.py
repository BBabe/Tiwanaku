'''

'''
import json
import os
## Parameters

size_max = 5
folder = '/home/chilly-ben/Documents/Créations/Code/tiwanaku'
name = 'tetris_forms.npy'
path = os.path.join(folder, name)

## Functions


def fun_neighbors(ter):
    i, j = ter
    return [[i, j-1], [i, j+1], [i-1, j], [i+1, j]]


def rec_all_mini_forms(ter, possible_coords0, region0, size_reg, list_forms0):
    possible_coords = possible_coords0.copy()
    region = region0.copy()
    list_forms = list_forms0.copy()

    # possible_coords.remove(ter)
    region.append(ter)

    if len(region) == size_reg:
        if region not in list_forms:
            list_forms.append(region)
    else:
        neighbors_all = fun_neighbors(ter)
        neighbors = [neighbor for neighbor in neighbors_all if neighbor not in possible_coords]
        if possible_coords:
            possible_coords.extend(neighbors)
        else:
            possible_coords = neighbors.copy()

        for ter in [terr for terr in possible_coords if terr not in region]:
            list_forms = rec_all_mini_forms(ter, possible_coords, region, size_reg, list_forms)

    return list_forms

##

list_final = []
for size_reg in range(1, size_max + 1):
    print(size_reg)
    ter = [0,0]
    possible_coords0 = [ter]
    region0 = []
    list_forms = []

    lis = rec_all_mini_forms(ter, possible_coords0, region0, size_reg, list_forms)
    list_final.append(lis)

##

with open(path, "w") as fp:
    json.dump(list_final, fp)

# with open(path, "r") as fp:
#     tetris_forms = json.load(fp

##

# plt.close('all')
# for region in lis:
#     xs = [region[i][0] for i in range(len(region))]
#     ys = [region[i][1] for i in range(len(region))]
#     plt.figure()
#     plt.plot(xs, ys, '*-')
#     plt.grid(True)
# plt.show()