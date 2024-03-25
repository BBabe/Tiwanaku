'''
For a given size of the board and a given maximum region size, compute all possible
[list of regions, list of cultures], with the following rules:
- The size of the regions can be anything between 1 and the maximum
- 2 equal cultures cannot be next to another, even diagonally
'''
import json
import time
import sys
from random import randrange, choice, shuffle
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
from multiprocess import Pool
# local
from find_forms_cultures_functions import fun_date, fun_permut, fun_init_while, fun_recursion, fun_first_couples,fun_time
from find_forms_cultures_functions import fun_copy, fun_update, fun_update_bis, fun_forms_in_remaining, fun_print, fun_init_small, fun_possibilities_recursif, fun_first_max

if __name__ == '__main__':
    ## Input parameters

    # Number of lines
    Ni = 5
    # Number of columns
    Nj = 5
    # Maximal region size
    size_max_reg = 5

    # Load already existing file
    bool_load = 0

    # Parallel computations: 1=yes, 0=no
    bool_parallel = 0
    # Number of parallel processes
    Ncpu = 11

    # Name of output file in output folder
    folder_out = 'test_data'
    str_today = fun_date()
    file_out = '{}_{}_{}_{}.json'.format(Ni, Nj, size_max_reg, str_today)

    ## Small computations and loading
    # Follow the number of elapsed seconds
    start = time.time()

    iz = range(Ni)
    jz = range(Nj)
    # All terrains coordinates
    coords_all = [[i, j] for i in iz for j in jz]

    # All possible region forms
    with open('data/tetris_forms.json', "r") as fp:
        tetris_forms = json.load(fp)

    # All possible sequences of cultures, for all region sizes
    permuts = fun_permut(size_max_reg)

    global_variables = [size_max_reg, permuts, tetris_forms, coords_all, bool_parallel, start]

    ## Initialize and run recursion

    if not bool_load:
        # Initialize lists for recursion
        remaining_ters0, changing_lists, first_couples = fun_init_while(iz, jz, coords_all)

        # Regular computations
        if not bool_parallel:
            ##


            def fun_recursion(remaining_ters, changing_lists, global_variables, region_cults):
                size_max_reg, permuts, tetris_forms, coords_all, bool_parallel, start = global_variables
                region0, cults = region_cults # Pair format to enable parallelisation

                # Preserve to-be-modified lists for other recursions
                list_regions, impossibilities, list_cultures = fun_copy(changing_lists)

                # Update lists with new region and cultures
                list_regions, list_cultures, remaining_ters = fun_update(region0, cults, list_regions, list_cultures, remaining_ters)

                # End of recursion
                if not remaining_ters:
                    return [list_regions, list_cultures]

                # Recursion
                else:
                    # Update list of impossible cultures on the board, following the neighborhood rule
                    impossibilities = fun_update_bis(region0, cults, impossibilities, coords_all)





                    # Always taking the first remaining terrain should allow to explore all possibilities
                    # i,j = remaining_ters[0]
                    social = [len(impossibilities[i][j]) for i,j in remaining_ters]
                    i,j = remaining_ters[social.index(max(social))]
                    # print(remaining_ters)
                    # input([i,j])

                    # Loop on the size of the new region (containing terrain [i,j]), limited by remaining size
                    size_max_tmp = min(len(remaining_ters), size_max_reg)
                    possible_sizes = list(range(1,size_max_tmp+1))
                    shuffle(possible_sizes)

                    for size_reg in possible_sizes:

                        # Loop on all forms of size_reg in remaining_ters
                        possible_forms = fun_forms_in_remaining(i,j, remaining_ters, size_reg, tetris_forms)
                        shuffle(possible_forms)
                        for region in possible_forms:
                            # fun_print(bool_parallel, list_regions, region0, region, start)

                            # ###############################################################################
                            # # Slower alternative to find possible cultures combinations, instead of what follows
                            # list_possibilities, current_cults, accepted_cults, cult, ind = fun_init_small(size_reg)
                            # list_possibilities = fun_possibilities_recursif([list_possibilities, current_cults, accepted_cults], cult, ind, region, impossibilities)
                            # shuffle(list_possibilities)
                            # for cults in list_possibilities:
                            #     print(2*len(list_regions)*' ', len(list_regions), region, '    ', cults)
                            #     list_boards = fun_recursion(remaining_ters, [list_regions, impossibilities, list_cultures], global_variables, [region, cults])
                            #     if list_boards:
                            #         return list_boards
                            # ###############################################################################
                            # Loop on all possible cultures order
                            premuts_tmp = permuts[size_reg-1]
                            shuffle(premuts_tmp)
                            for cults in premuts_tmp:

                                # Check if current cultures order avoids impossibilities
                                for ind_cult, cult in enumerate(cults):
                                    a,b = region[ind_cult]
                                    if cult in impossibilities[a][b]:
                                        break # terminate computations from the first impossibility
                                else: # if no break
                                    print(2*len(list_regions)*' ', len(list_regions), region, '    ', cults)
                                    list_boards = fun_recursion(remaining_ters, [list_regions, impossibilities, list_cultures], global_variables, [region, cults])
                            # ###############################################################################

                    return []

                ##

            # Start with a list of all possible regions-cultures for terrain [i,j]
            i = randrange(Ni)
            j = randrange(Nj)
            max_couples = fun_first_max(i,j, size_max_reg, coords_all, permuts, tetris_forms)
            shuffle(max_couples)
            print('Starting recursion...')
            compteur = 0
            list_boards = []
            while compteur<len(max_couples) and not list_boards:
                regions, cultures = max_couples[compteur]
                print(regions, '    ', cultures)
                # print(compteur)
                list_boards = fun_recursion(remaining_ters0, changing_lists, global_variables, [regions, cultures])
                compteur += 1
                input()

            list_regions, list_cultures = list_boards

            ##

        # Parallel computations
        else:

            # Parallel computations
            p = Pool(Ncpu)
            results = p.map(partial(fun_recursion, remaining_ters0, changing_lists, global_variables), first_couples)
            p.close()
            p.join()

            # Same format as non-parallel computations
            list_results = []
            for res in results:
                list_results.extend(res) # extend instead of append rule in formation of results

        ## Save result

        # with open('{}/{}'.format(folder_out, file_out), "w") as fp:
        #     json.dump(list_results, fp)

        print(fun_time(start))

    ## Load

    else:
        import glob as glob
        import os

        list_paths = glob.glob(os.path.join(folder_out, file_out[:5] + '*'))
        if list_paths:
            path = list_paths[0]
            with open(path, "r") as fp:
                list_results = json.load(fp)

    ## Prints of result

    # print(len(list_results))
    # for ter,cult in list_results:
    #     print(ter)
    #     print(cult)
    #     print()

    ## Plot

    board = np.full((Ni, Nj), 0)
    for ind, region in enumerate(list_regions):
        for i,j in region:
            board[i,j] = ind

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

