# CS3243 Assignment 2 Sudoku CSP
# Group 09
# Authors: Tham Si Mun (A0171711N), Jack Chen Yu Jie (A0171233R)
# Algo: AC3, Backtracking with MRV and LCV

import sys
import copy

rows = "123456789"
cols = "ABCDEFGHI"

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = list()
        # make the puzzle a flatlist
        self.puzzle = [item for sublist in puzzle for item in sublist]

        # variables
        self.coords = list()
        self.coords = self.create_coordinates()
        # print(self.coords)

        # domains
        self.domains = dict()
        self.domains = self.generate_domains()

        # for i in self.coords:
            # print(self.domains[i])

        # related coords
        self.peers = dict()
        self.peers = self.generate_peers_list()

        # constraints
        self.binary_constraints = list()
        self.binary_constraints = self.generate_binary_constraints()

        # self.related_coords = dict()
        # self.related_coords = self.generate_related_coords()

        # flat_list = []
        #     for sublist in l:
        #         for item in sublist:
        #             flat_list.append(item)

        # self.ans is a list of lists
        self.ans = copy.deepcopy(puzzle)

    def solve(self):
        ac3_result = self.AC3()

        #  by AC3
        if self.check_complete() and ac3_result:
            self.ans = self.return_solved_puzzle()
        # cant be solved by AC3, use backtracking
        else:
            assignment = {}

            # for the already known values
            for coord in self.coords:
                if len(self.domains[coord]) == 1:
                    assignment[coord] = self.domains[coord][0]
            
            # start backtracking
            assignment = self.recursive_backtrack(assignment)
            
            # merge the computed values for the cells at one place
            for coord in self.domains:
                if len(coord) > 1:
                    self.domains[coord] = assignment[coord] 
            
            if assignment:
                self.ans = self.return_solved_puzzle();

        # don't print anything here. just return the answer
        # self.ans is a list of lists
        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY

    '''
        Method to create list of coordinates representing variables
    '''
    def create_coordinates(self):
        return self.find_list(cols, rows)

    '''
       Method to generate domains for each variable
       Returns a dictionary with key as variable and value as a list of values in domain
    '''
    def generate_domains(self):
        domains = dict()

        for i in range(len(self.coords)):
            if self.puzzle[i] == 0:
                domains[self.coords[i]] = list(range(1,10))
            else:
                domains[self.coords[i]] = [self.puzzle[i]]

        # for coord in self.coords:
        #     print(domains[coord])

        return domains

    def find_list(self, X, Y):
        return [x + y for x in X for y in Y]

    '''
        Method to generate list of neighbouring variables for each variable
        Returns a dictionary with key as the variable and value as the set of neighbouring variables
    '''
    def generate_peers_list(self):
        row_list = [self.find_list(col, rows) for col in cols]
        col_list = [self.find_list(cols, row) for row in rows]
        box_list = [self.find_list(col_box, row_box) for col_box in ('ABC', 'DEF', 'GHI') for row_box in ('123', '456', '789')]
        #27 lists
        lists_all_diff = row_list + col_list + box_list

        map_list_all_diff = dict((coord, [l for l in lists_all_diff if coord in l]) for coord in self.coords)

        peers_list = dict()

        # make values unique and remove the duplicates and itself from the list
        for coord in self.coords:
            flat_list = [item for sublist in map_list_all_diff[coord] for item in sublist]
            flat_set = set(flat_list)
            flat_set.remove(coord)
            peers_list[coord] = flat_set

        return peers_list

    '''
        Method to generate list of binary constraints (Var1, Var2)
    '''
    def generate_binary_constraints(self):
        return [(variable, peer) for variable in self.coords for peer in self.peers[variable]]

    '''
        Method to check if the Sudoku is complete
        Criteria for being complete: Domain of each variable only has one value
    '''
    def check_complete(self):
        for coords, domain in self.domains.items():
            if len(domain) > 1:
                return False
        return True

    '''
        AC3 algorithm
    '''
    def AC3(self):
        # queue = list(self.binary_constraints)
        queue = self.binary_constraints

        while queue:

            (x, y) = queue.pop(0)

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for i in self.peers[x]:
                    if i != x:
                        queue.append((i,x))

        return True

    '''
        Revise method to be used in AC3
    '''
    def revise(self, x, y):

        revised = False

        for i in self.domains[x]:

            if not any([self.is_different(i, j) for j in self.domains[y]]):
            
                # then remove i from x's domain
                self.domains[x].remove(i)
                revised = True

        return revised

    '''
        Checks whether i and j are different values
    '''
    def is_different(self,i, j):
        return i != j

    '''
        Method to assign values to sudoku variables 
        using backtracking algorithm recursively
    '''
    def recursive_backtrack(self, assignment):
        if len(assignment) == len(self.coords):
            return assignment

        # Select the variable to assign next
        coord = self.select_unassigned_coord(assignment)
        domain = copy.deepcopy(self.domains)

        # Select the least constraining values for variable
        for x in self.order_domain_values(coord):
            if self.consistent(assignment, coord, x):
                assignment[coord] = x
                inferences = {}
                # Begin forward checking
                inferences = self.inference(assignment, inferences, coord, x)

                if inferences != "FAILURE":
                    result = self.recursive_backtrack(assignment)
                    if result != "FAILURE":
                        return result
                del assignment[coord]
                self.domains.update(domain)
        return "FAILURE"

    '''
        Method to check for consistency between two variables
    '''
    def consistent(self, assignment, coord, value):
        consistency = True
        
        for curr_coord, curr_value in assignment.items():

            # if the values are equal and the coords are peers, not consistent
            if curr_value == value and curr_coord in self.peers[coord]:
                consistency = False

        return consistency

    '''
        Minimum Remaining Value: 
        Choose next variable to assign value by priority of the variable having
        fewest value left to assign
    '''
    def select_unassigned_coord(self, assignment):
        unassigned_coord = []

        for coord in self.coords:
            if coord not in assignment:
                unassigned_coord.append(coord)

        return min(unassigned_coord, key=(lambda coord: len(self.domains[coord])))

    '''
        Least constraining value: 
        Value that rules out the fewest
        choices for neighbouring variables in sudoku   
    '''
    def order_domain_values(self, coord):
        if len(self.domains[coord]) == 1:
            return self.domains[coord]

        return sorted(self.domains[coord], key=(lambda value: self.count_conflicts(coord, value)))

    '''
        Method to count number of conflicts with other peers' domains
        for this particular value
    '''
    def count_conflicts(self, coord, value):
        total = 0
        for peer in self.peers[coord]:
            # rules out value for peers
            if len(self.domains[peer]) > 1 and value in self.domains[peer]:
                total += 1

        return total

    '''
        Inference, to be used with backtracking search
    '''
    def inference(self, assignment, inferences, coord, value):
        inferences[coord] = value

        for peer in self.peers[coord]:
            # If neighbouring variable is not assigned yet and the value that
            # is to be assigned to current variable is in domain of the neighbouring variable
            if peer not in assignment and value in self.domains[peer]:
                # We check that this is not the only value left in the neighbouring
                # variable's domain, if so, this assignment fails
                if len(self.domains[peer]) == 1:
                    return "FAILURE"

                # If it is not the last value in domain of neighbouring variable, remove this value
                self.domains[peer].remove(value)
                remaining = self.domains[peer]

                if len(remaining) == 1:
                    check = self.inference(assignment, inferences, peer, remaining)
                    if check == "FAILURE":
                        return "FAILURE"

        return inferences

    '''
        Method to return the solved puzzle in the form of a 
        list of lists
    '''
    def return_solved_puzzle(self):
        puzzle = [[0 for i in range(9)] for j in range(9)]
        i = 0
        j = 0

        for c in cols:
            j = 0
            for r in rows:
                puzzle[i][j] = self.domains[c+r]
                j += 1
                if j > 8:
                    break
            i += 1
            if i > 8:
                break

        return puzzle


if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
