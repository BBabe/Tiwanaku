'''
For a given size of the board and a given maximum region size, compute all possible
[list of regions, list of cultures], with the following rules:
- The size of the regions can be anything between 1 and the maximum
- 2 equal cultures cannot be next to another, even diagonally

'''
import json
import time
from functools import partial
from multiprocess import Pool
# local
from find_forms_cultures_functions import fun_date, fun_permut, fun_init, fun_recursion, fun_first_couples,fun_time

if __name__ == '__main__':
    ## Input parameters

    # Number of lines
    Ni = 3
    # Number of columns
    Nj = 3
    # Maximal region size
    size_max_reg = 5

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

    # Initialize lists for recursion
    remaining_ters0, changing_lists, first_couples = fun_init(iz, jz, coords_all)

    # Regular computations
    if not bool_parallel:
        list_results = fun_recursion(remaining_ters0, changing_lists, global_variables, first_couples)

    # Parallel computations
    else:
        # Start with a list of all possible regions-cultures for terrain [0,0]
        first_couples = fun_first_couples(size_max_reg, coords_all, permuts)

        # Parallel computations
        p = Pool(Ncpu)
        results = p.map(partial(fun_recursion, changing_lists, global_variables), first_couples)
        p.close()
        p.join()

        # Same format as non-parallel computations
        list_results = []
        for res in results:
            list_results.extend(res) # extend instead of append rule in formation of results

    ## Save result

    with open('{}/{}'.format(folder_out, file_out), "w") as fp:
        json.dump(list_results, fp)

    print(fun_time(start))

    ## Prints of result

    print(len(list_results))
    # for ter,cult in list_results:
    #     print(ter)
    #     print(cult)
    #     print()