import numpy as np


def gen_covers(sudoku):
    chars = tuple(range(9))
    used_cells = {(i//9, i%9) for i, x in enumerate(sudoku.flat) if x != 0}

    possibilities = {
        poss: {
            (poss[0], poss[1], -1, -1),       # Row, Column
            (poss[0], -1, poss[2], -1),       # Row, Number
            (-1, poss[1], poss[2], -1),       # Column, Number
            (-1, -1, poss[2], poss[0]//3 * 3 + poss[1]//3)    # Box, Number
        }
        for poss in 
            ((a,b,c+1) for a in chars for b in chars for c in chars)
        if poss[:2] not in
            used_cells
    }

    possibilities |= {
        (i//9, i%9, x): {
            (i//9, i%9, -1, -1),      # Row, Column
            (i//9, -1, x, -1),      # Row, Number
            (-1, i%9, x, -1),       # Column, Number
            (-1, -1, x, i//27 * 3 + i%9//3)   # Box, Number
        }
        for i, x in enumerate(sudoku.flat)
        if x != 0
    }

    constraints = {
        code:set()
        for a in chars for b in chars
        for code in (
            (a, b, -1, -1),
            (-1, a, b+1, -1),
            (a, -1, b+1, -1),
            (-1, -1, b+1, a)
        )
    }

    for poss in possibilities:
        for const in possibilities[poss]:
            constraints[const].add(poss)

    return possibilities, constraints


def algoX(cell_consts, const_cells, part_sol = None):
    if part_sol is None:
        part_sol = []
    if not const_cells:
        return part_sol

    # 1. This constraint is satisfied by the fewest remaining available cells - like singletons
    const = min(const_cells, key=lambda x: len(const_cells[x]))
    if not len(const_cells[const]):
        return None

    part_sol.append("")
    # 2. Choose a possibility from this to try
    for poss in const_cells[const]:
        # 3.
        part_sol[-1] = poss

        bad_consts, bad_cells = set(), set()
        # 4. For each constraint this cell satisfies.
        for bad_const in cell_consts[poss]:
            # For each cell which satisfies this constraint, remove the cell
            for bad_cell in const_cells[bad_const]:
                bad_cells.add(bad_cell)
            bad_consts.add(bad_const)
        
        res = algoX(cell_consts,
            {x:const_cells[x].difference(bad_cells) for x in const_cells if x not in bad_consts},
            part_sol)
        if res is not None:
            return res


def sudoku_solver(sudoku):
    solved_sudoku = np.ndarray(sudoku.shape, np.int8)
    poss_row, const_row = gen_covers(sudoku)

    if (result := algoX(poss_row, const_row)) is not None:
        for poss in result:
            solved_sudoku[poss[0], poss[1]] = poss[2]
    else:
        solved_sudoku.fill(-1)

    return solved_sudoku


def tests():
    import time
    difficulties = ['very_easy', 'easy', 'medium', 'hard']
    # difficulties = [difficulties[-1]]

    for difficulty in difficulties:
        print(f"Testing {difficulty} sudokus")

        worst_case  = -1
        total_time  = 0
        num_suds    = 0

        sudokus = np.load(f"data/{difficulty}_puzzle.npy")
        solutions = np.load(f"data/{difficulty}_solution.npy")
        
        count = 0
        for i in range(len(sudokus)):
            sudoku = sudokus[i].copy()
            print(f"This is {difficulty} sudoku number", i)
            print(sudoku)
            
            try:
                start_time = time.process_time()
                your_solution = sudoku_solver(sudoku)
                end_time = time.process_time()
            except Exception as e:
                print(f"It was broken by {difficulty} sudoku number", i)
                raise e

            print(f"This is your solution for {difficulty} sudoku number", i)
            print(your_solution)
            
            print("Is your solution correct?")
            if np.array_equal(your_solution, solutions[i]):
                print("Yes! Correct solution.")
                count += 1
            else:
                print("No, the correct solution is:")
                print(solutions[i])

            time_taken = end_time-start_time
            print("This sudoku took", time_taken, "seconds to solve.\n")
            total_time += time_taken
            worst_case = max(worst_case, time_taken)
            num_suds += 1


        print(f"{count}/{len(sudokus)} {difficulty} sudokus correct")
        print(f"\nAvg Time: {total_time / num_suds}\nWorst Case: {worst_case}")

        if count < len(sudokus):
            break


# import cProfile
# cProfile.run("tests()", sort="time")

tests()