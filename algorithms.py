import pandas as pd
from enum import Enum
from math import sqrt
import random
import time
class SOLUTION(Enum):
    STOCHASTIC_SWAP = 'stochastic_swap'
    TWO_OPT = 'two_opt'
class Grasp():
    def __init__(self, file_path, sol_type=SOLUTION.STOCHASTIC_SWAP.value):
        self.number_iteration = 1000
        self.nodes = read_data(file_path)
        self.solution_type = sol_type
        
    def launch(self, alpha, early_stop):
        """
        Khung của chương trình.
        Tìm kiếm lời giải number_iteration lần. Update lời giải và cost tương ứng nếu có lời giải tốt hơn
        :param early_stop: Số lần tối đa để dừng tìm kiếm local_search
        :return: alpha,  best_cost
        """
        number_iteration = self.number_iteration
        start = time.time()

        best_cost = float('inf')
        best_solution = None

        while number_iteration > 0:
            print('ITERATION %d' % number_iteration)
            number_iteration -= 1
            new_solution, new_cost = self.__construct_greedy_solution(alpha)
            new_solution, new_cost = self.__local_search(new_solution, new_cost, early_stop)

            if new_cost < best_cost:
                best_cost = new_cost
                best_solution = new_solution
                print('New solution found:\nCost:%.2f' % best_cost)

        stop = time.time()

        running_time = stop - start

        print('Best cost: %.2f, Elapsed: %.2f' % (best_cost, running_time))
        print('Best solution: %s' % best_solution)
        return alpha, best_cost
    
    def __construct_greedy_solution(self, alpha):
        """
        Khởi tạo một lời giải tham lam
        :return: Một lời giải bán phần và cost tương ứng
        """
        nodes = self.nodes
        solution = []
        nodes_number = len(nodes)
        visited_nodes = [0] * nodes_number
        chosen_node_index = random.randrange(0, nodes_number)
        solution.append(chosen_node_index)  # chọn node đầu tiên ngẫu nhiên
        visited_nodes[chosen_node_index] = 1

        # Thêm nodes vào solution cho đến khi số lượng node trong solution bằng với input
        while len(solution) < nodes_number:
            cost_list = []
            max_cost = 0
            min_cost = float('inf')

            for index in range(nodes_number):
                if visited_nodes[index] == 0:
                    cost = distance(nodes[solution[-1]], nodes[index])
                    max_cost = cost if cost > max_cost else max_cost
                    min_cost = cost if cost < min_cost else min_cost
                    cost_list.append((index, cost))

            rcl = []

            for index, cost in cost_list:
                if cost <= min_cost + alpha*(max_cost-min_cost):
                    rcl.append(index)

            selected_node_index = rcl[random.randrange(0, len(rcl))]
            solution.append(selected_node_index)
            visited_nodes[selected_node_index] = 1

        new_cost = self.__tour_cost(solution)

        return solution, new_cost
    
    def __local_search(self, solution, cost, early_stop):
        """
        Giải thuật local search để phát hiện ngẫu nhiên những liền kề xung quanh lời giải bán phần
        :param solution: một lời giải bán phần
        :param cost: cost tương ứng với một lời giải
        :param early_stop: local search sẽ dừng nếu cost ko cải thiện sau một số lần early_stop chạy
        :return: a new solution, corresponding cost
        """

        count = 0

        while count < early_stop:
            if self.solution_type == 'stochastic_swap':
                new_solution = self.__stochastic_swap(solution)  # randomly swap two edges to explore the possible neighbors.
            else:
                new_solution = self.__two_opt(solution)
            new_cost = self.__tour_cost(new_solution)  # calculate the total cost of a solution

            #  update the solution and cost if a better solution is found
            if new_cost < cost:
                solution = new_solution
                cost = new_cost
                count = 0
            else:
                count += 1

        return solution, cost

    def __tour_cost(self, solution):
        """
        tính toán tổng khoảng cách euclid của một lời giải
        :param solution: Một lời giải chứa index của các node
        :return: total distance of a route
        """
        nodes = self.nodes
        total_distance = 0

        for index in range(len(solution)):
            start_index = solution[index]
            end_index = solution[(index + 1) % len(solution)]

            total_distance += distance(nodes[start_index], nodes[end_index])

        return total_distance

    @staticmethod
    def __stochastic_swap(solution):
        """
        Đổi 2 cạnh trên một đường đi
        Ngẫu nhiên chọn 2 node khác nhau và không liền kề. Thay đổi vị trí 2 node và đường đi giữa 2 node

        :param solution: Một lời giải chứa index của các node
        :return: a new solution
        """

        sol_copy = solution[:]  # tạo một copy
        sol_size = len(solution)

        node_1_index = random.randrange(0, sol_size)  # randomly select a node
        node_2_index = random.randrange(0, sol_size)  # randomly select another node

        exclude_set = {node_1_index}  # create a forbidden set to guarantee node 2 is not node 1 or the neighbor of node1

        #  the rules exclude set
        if node_1_index == 0:
            exclude_set.add(sol_size-1)
        else:
            exclude_set.add(node_1_index-1)

        if node_1_index == sol_size - 1:
            exclude_set.add(0)
        else:
            exclude_set.add(node_1_index+1)

        #  if the selected node 2 is in the exclude set, select again
        while node_2_index in exclude_set:
            node_2_index = random.randrange(0, sol_size)

        #  to guarantee that node 1 index < node 2 index
        if node_2_index < node_1_index:
            node_1_index, node_2_index = node_2_index, node_1_index

        #  reversed the route between two selected nodes
        sol_copy[node_1_index:node_2_index] = reversed(sol_copy[node_1_index:node_2_index])

        return sol_copy
    
    def __two_opt(self, solution):
        improved = True
        best_sol = solution
        best_cost = self.__tour_cost(solution)
        while improved:
            improved = False
            for i in range(1, len(solution) - 2):
                for j in range(i + 2, len(solution)):
                    new_sol = solution.copy()
                    new_sol[i:j] = solution[j - 1:i - 1:-1]
                    new_cost = self.__tour_cost(new_sol)
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_sol = new_sol
                        improved = True
                        break
                if improved:
                    break
            solution = best_sol
        
        return best_sol
            
                        


"""
HELPER
"""
def distance(node_1, node_2):
    """
    Tính khoảng cách giữa 2 nodes
    :param node_1: a node
    :param node_2: another node
    :return: distance between two nodes
    """

    distance_two_nodes = 0

    for x, x1 in zip(node_1, node_2):
        distance_two_nodes += (x - x1) * (x - x1)
    return sqrt(distance_two_nodes)

def read_data(file):
    """
    Đọc data từ file input
    :return: a list of the data file
    """

    f = pd.read_csv(file, sep='\s+')
    f = pd.DataFrame(f).to_numpy().tolist()
    return f