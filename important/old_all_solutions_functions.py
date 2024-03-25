import copy
import time
from itertools import permutations
import datetime as dt

## Small functions


def fun_date():
    today = dt.datetime.now()
    str_today = str(today)[:10] + '_' + str(today)[11:13] + '-' + str(today)[14:16]
    return str_today


def fun_permut(size_max_reg):
    ''' All possible sequences of cultures, for all region sizes '''
    permuts = []
    for size in range(1, size_max_reg+1):
        permuts.append([[ind for ind in permut] for permut in permutations(range(1,size+1))]) # permutations function yields tuples
    return permuts


def fun_init(iz, jz, coords_all):
    ''' Initialize lists for recursion '''
    impossibilities0 = [[[] for j in jz] for i in iz] # careful on the order of i and j if different
    list_cultures0 = [[0 for j in jz] for i in iz] # 0 instead of [] to prepare the integer type
    remaining_ters0 = coords_all.copy()
    list_regions0 = []
    list_boards0 = []
    region = []
    cults = []
    return remaining_ters0, [list_regions0, list_boards0, impossibilities0, list_cultures0], [region, cults]


def fun_init_while(iz, jz, coords_all):
    ''' Initialize lists for recursion '''
    impossibilities0 = [[[] for j in jz] for i in iz] # careful on the order of i and j if different
    list_cultures0 = [[0 for j in jz] for i in iz] # 0 instead of [] to prepare the integer type
    remaining_ters0 = coords_all.copy()
    list_regions0 = []
    region = []
    cults = []
    return remaining_ters0, [list_regions0, impossibilities0, list_cultures0], [region, cults]


def fun_first_max(i,j, size_max_reg, coords_all, permuts, tetris_forms):
    ''' For parallel computations, start with a list of all possible regions-cultures for terrain [0,0] '''
    first_couples = []
    # All possible forms of size_reg in the board from terrain [0,0]
    forms_size = fun_forms_in_remaining(i,j, coords_all, size_max_reg, tetris_forms, [])
    # Combine each form with all possible cultures orders
    for region in forms_size:
        for cults in permuts[size_max_reg-1]:
            first_couples.append([region, cults])
    return first_couples


def fun_first_couples(size_max_reg, coords_all, permuts, tetris_forms):
    ''' For parallel computations, start with a list of all possible regions-cultures for terrain [0,0] '''
    i = j = 0
    first_couples = []
    # Loop on size of first region
    for size_reg in range(1,size_max_reg+1):
        # All possible forms of size_reg in the board from terrain [0,0]
        forms_size = fun_forms_in_remaining(i,j, coords_all, size_reg, tetris_forms, [])
        # Combine each form with all possible cultures orders
        for region in forms_size:
            for cults in permuts[size_reg-1]:
                first_couples.append([region, cults])
    return first_couples


## Recursion function


def fun_recursion(remaining_ters, changing_lists, global_variables, region_cults):
    '''
    For a given size of the board and a given maximum region size, compute all possible
    [list of regions, list of cultures].

    Recursion functions work as follows:
    - make a copy of lists to be updated
    - update lists
    - condition of end of recursion
    - recursion: loops on diverging possibilities

    This function calls itself whenever a new region is chosen. The loops are on:
    - the possible sizes of the region
    - the possible forms of a region this size
    - the possible cultures combinations of such a form, considering the impossibilities

    '''
    size_max_reg, permuts, tetris_forms, coords_all, bool_parallel, start = global_variables
    region0, cults = region_cults # Pair format to enable parallelisation

    # Preserve to-be-modified lists for other recursions
    list_regions, list_boards, impossibilities, list_cultures = fun_copy(changing_lists)

    # Update lists with new region and cultures
    list_regions, list_cultures, remaining_ters = fun_update(region0, cults, list_regions, list_cultures, remaining_ters)

    # End of recursion
    if not remaining_ters:
        list_boards.append([list_regions, list_cultures])
        # print(list_regions)
        # for i in range(len(list_cultures)):
        #     print(list_cultures[i])
        # print()

    # Recursion
    else:
        # Update list of impossible cultures on the board, following the neighborhood rule
        impossibilities = fun_update_bis(region0, cults, impossibilities, coords_all)

        # Always taking the first remaining terrain should allow to explore all possibilities
        i,j = remaining_ters[0]

        # Loop on the size of the new region (containing terrain [i,j]), limited by remaining size
        size_max_tmp = min(len(remaining_ters), size_max_reg)
        for size_reg in range(1,size_max_tmp+1):

            # Loop on all forms of size_reg in remaining_ters
            possible_forms = fun_forms_in_remaining(i,j, remaining_ters, size_reg, tetris_forms, list_cultures)
            for region in possible_forms:
                # fun_print(bool_parallel, list_regions, region0, region, start)

                # # Slower alternative to find possible cultures combinations, instead of what follows
                # list_possibilities, current_cults, accepted_cults, cult, ind = fun_init_small(size_reg)
                # list_possibilities = fun_possibilities_recursif([list_possibilities, current_cults, accepted_cults], cult, ind, region, impossibilities)
                # for cults in list_possibilities:
                #     list_boards = fun_recursion(remaining_ters, [list_regions, list_boards, impossibilities, list_cultures], global_variables, [region, cults])

                # Loop on all possible cultures order
                for cults in permuts[size_reg-1]:

                    # Check if current cultures order avoids impossibilities
                    for ind_cult, cult in enumerate(cults):
                        a,b = region[ind_cult]
                        if cult in impossibilities[a][b]:
                            break # terminate computations from the first impossibility

                    else: # if no break
                        list_boards = fun_recursion(remaining_ters, [list_regions, list_boards, impossibilities, list_cultures], global_variables, [region, cults])


    return list_boards

##


def fun_recursion_np(remaining_ters, impossibilities, changing_lists, global_variables, region_cults):
    '''
    For a given size of the board and a given maximum region size, compute all possible
    [list of regions, list of cultures].

    Recursion functions work as follows:
    - make a copy of lists to be updated
    - update lists
    - condition of end of recursion
    - recursion: loops on diverging possibilities

    This function calls itself whenever a new region is chosen. The loops are on:
    - the possible sizes of the region
    - the possible forms of a region this size
    - the possible cultures combinations of such a form, considering the impossibilities

    '''
    size_max_reg, permuts, tetris_forms, coords_all, bool_parallel, start = global_variables
    region0, cults = region_cults # Pair format to enable parallelisation

    # Preserve to-be-modified lists for other recursions
    list_regions, list_boards, list_cultures = fun_copy(changing_lists)

    # Update lists with new region and cultures
    list_regions, list_cultures, remaining_ters = fun_update(region0, cults, list_regions, list_cultures, remaining_ters)

    # End of recursion
    if not remaining_ters:
        list_boards.append([list_regions, list_cultures])
        # print(list_regions)
        # for i in range(len(list_cultures)):
        #     print(list_cultures[i])
        # print()

    # Recursion
    else:
        # Update list of impossible cultures on the board, following the neighborhood rule
        impossibilities = fun_update_bis(region0, cults, impossibilities, coords_all)

        # Always taking the first remaining terrain should allow to explore all possibilities
        i,j = remaining_ters[0]

        # Loop on the size of the new region (containing terrain [i,j]), limited by remaining size
        size_max_tmp = min(len(remaining_ters), size_max_reg)
        for size_reg in range(1,size_max_tmp+1):

            # Loop on all forms of size_reg in remaining_ters
            possible_forms = fun_forms_in_remaining(i,j, remaining_ters, size_reg, tetris_forms, list_cultures)
            for region in possible_forms:
                # fun_print(bool_parallel, list_regions, region0, region, start)

                # # Slower alternative to find possible cultures combinations, instead of what follows
                # list_possibilities, current_cults, accepted_cults, cult, ind = fun_init_small(size_reg)
                # list_possibilities = fun_possibilities_recursif([list_possibilities, current_cults, accepted_cults], cult, ind, region, impossibilities)
                # for cults in list_possibilities:
                #     list_boards = fun_recursion(remaining_ters, [list_regions, list_boards, impossibilities, list_cultures], global_variables, [region, cults])

                # Loop on all possible cultures order
                for cults in permuts[size_reg-1]:

                    # Check if current cultures order avoids impossibilities
                    for ind_cult, cult in enumerate(cults):
                        a,b = region[ind_cult]
                        if cult in impossibilities[a][b]:
                            break # terminate computations from the first impossibility

                    else: # if no break
                        list_boards = fun_recursion(remaining_ters, impossibilities, [list_regions, list_boards, list_cultures], global_variables, [region, cults])


    return list_boards


## Functions used in recursion


def fun_copy(changing_lists):
    ''' Preserve to-be-modified lists for other recursions '''
    copy_list = []
    for var in changing_lists:
        copy_list.append(copy.deepcopy(var))
    return copy_list
    # list_regions0, list_boards0, impossibilities0, list_cultures0 = changing_lists
    # return copy.deepcopy(list_regions0), copy.deepcopy(list_boards0), copy.deepcopy(impossibilities0), copy.deepcopy(list_cultures0)


def fun_update(region, cults, list_regions, list_cultures, remaining_ters):
    ''' Update lists with new region and cultures '''
    if region: # valid for first recursion
        # Add region to current list
        list_regions.append(region)
        # Terrains not used yet by list of regions
        remaining_ters = [ter for ter in remaining_ters if ter not in region] # no need to use a copy of this list

        for ter, cult in zip(region, cults):
            i,j = ter
            # Add culture to list
            list_cultures[i][j] = cult
    return list_regions, list_cultures, remaining_ters


def fun_update_bis(region, cults, impossibilities, coords_all):
    '''
    Update list of impossible cultures on the board, following the neighborhood rule
    This list is updated separately from the others to limit number of computations
    '''
    if region: # valid for first recursion
        for ter, cult in zip(region, cults):
            impossibilities = fun_update_small(ter, cult, impossibilities, coords_all)
    return impossibilities


def fun_update_small(ter, cult, impossibilities, coords_all):
    '''
    Update list of impossible cultures on the board, following the neighborhood rule
    This list is updated separately from the others to limit number of computations
    '''
    i,j = ter
    neighbors = fun_neighbors(i,j)
    impos_tmp = [ter for ter in neighbors if ter in coords_all] # neighbors which are on the board
    for a,b in impos_tmp: # i,j could be re-used
        if cult not in impossibilities[a][b]: # avoid having same culture several times
            impossibilities[a][b].append(cult)
    return impossibilities


def fun_neighbors(i,j):
    ''' Coordinates of all 8 neighbors of terrain [i,j] '''
    return [[i+x, j+y] for x in [-1,0,1] for y in [-1,0,1]] # list also contains ter, which is not a problem


def fun_forms_in_remaining(i,j, remaining_ters, size_reg, tetris_forms, list_cultures):
    ''' All forms of size_reg in remaining_ters (and containing terrain [i,j] '''
    # For each form of shape size_reg, terrain [i,j] could be anywhere
    all_forms = [[[a+i,b+j] for a,b in reg] for reg in tetris_forms[size_reg-1][:]]

    # Keep only forms in remaining_ters
    possible_forms = []
    for reg in all_forms:
        if all(item in remaining_ters for item in reg):

            # Different initial forms, if starting from a different terrain, can be the same
            reg.sort() # list order matters
            if reg not in possible_forms:

                bool_pb = False
                # if sum([sum(cultures_already[i]) for i in range(len(cultures_already))]):
                if list_cultures:
                    cultures_already = [list_cultures[i][j] for i,j in reg if list_cultures[i][j]]
                    if cultures_already:
                        cultures_already = sorted(cultures_already, reverse=True)
                        if cultures_already[0] > size_reg:
                            bool_pb = True
                        elif len(cultures_already) > 1:
                            ind = 0
                            while ind < len(cultures_already)-1 and not bool_pb:
                                bool_pb = (cultures_already[ind] == cultures_already[ind+1])
                                ind += 1
                if not bool_pb:

                    possible_forms.append(reg)
    return possible_forms


def fun_print(bool_parallel, list_regions, region0, region, start):
    ''' Prints to follow progression. When parallelisation is used for bigger problems, more frequent prints '''
    if len(list_regions) == bool_parallel: # avoid double check (if bool) + (if len)
        elapsed_time = fun_time(start)
        print(region0, region, elapsed_time, sep = '     ') # region0 allows to print even if not same format


def fun_time(start):
    time_format = '%H:%M:%S'
    Nseconds = int(time.time()-start)
    elapsed_time = str(time.strftime(time_format, time.gmtime(Nseconds)))
    return elapsed_time


def fun_init_small(size_reg):
    ''' Initialize lists for fun_possibilities_recursif '''
    list_possibilities = []
    current_cults = list(range(1, size_reg+1))
    accepted_cults = []
    cult = 0
    ind = 0
    return list_possibilities, current_cults, accepted_cults, cult, ind


def fun_possibilities_recursif(changing_lists, cult, ind, region, impossibilities):
    '''
    Other way to test all possible cultures orders corresponding to a region (considering impossibilities):
    instead of testing the compability of each combinations with the impossibilities, the possible combinations are built recursively, thus maybe avoiding computation repetitions.
    '''
    # Preserve to-be-modified lists for other recursions
    list_possibilities, current_cults, accepted_cults = fun_copy(changing_lists)

    # Update lists with current culture
    if cult:
        accepted_cults.append(cult)
        current_cults.remove(cult)

    # End of recursion
    if not current_cults:
        list_possibilities.append(accepted_cults)

    # Recursion
    else:
        i,j = region[ind]
        # Loop on possible cultures
        possible_cults = [cult for cult in current_cults if cult not in impossibilities[i][j]]
        for cult in possible_cults:
            list_possibilities = fun_possibilities_recursif([list_possibilities, current_cults, accepted_cults], cult, ind+1, region, impossibilities)

    return list_possibilities

