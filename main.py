import argparse
import sys
import os
import numpy as np
import csv

from algorithms import Grasp, SOLUTION
    
MAX_ALPHA = 1
ALPHA_INTERVAL = 5

def main():
    """
    Main function.
    Thử với 5 số alpha khác nhau từ 0:0.2:1
    """
    parser = argparse.ArgumentParser(description='argument for GRASP algorithm')
    parser.add_argument('--file_path', type=str, help='path to input file')
    parser.add_argument('--num_expr', type=int, help='number of experiment')
    parser.add_argument('--search_type', type=int, help='number of indicate local search type')
    
    args = parser.parse_args()
    
    if not args.num_expr:
        print('Error: --num_expr argument is required')
        sys.exit(1)
    
    if not args.file_path:
        print('Error: --file_path argument is required')
        sys.exit(1)
        
    experiment_number = args.num_expr  # run the experiment 30 times
    file_path = args.file_path
    search_type = SOLUTION.TWO_OPT.value if args.search_type == 1 else SOLUTION.STOCHASTIC_SWAP.value
        
    alpha_list = []
    cost_list = []
    early_stop_list = []
    grasp = Grasp(file_path, search_type)
    
    for index in range(6):
        alpha = MAX_ALPHA / ALPHA_INTERVAL * index
        for early_stop in np.arange(50, 300, 50):
            temp_cost = []
            # calculate the mean cost of each alpha value
            for i in range(experiment_number):
                _, best_cost = grasp.launch(alpha, early_stop)
                temp_cost.append(best_cost)
            cost_mean = sum(temp_cost)/len(temp_cost)

            early_stop_list.append(early_stop)
            cost_list.append(cost_mean)
        
        alpha_list.append(alpha)
        write_to_file('GRASP_result_early_stop.csv', alpha, early_stop_list, cost_list)
        cost_list = []
        early_stop_list = []

def write_to_file(file, alpha, early_stops, costs):
    if not os.path.exists(file):
        with open(file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(['alpha', 'early_stop', 'cost'])
            for early_stop, cost in zip(early_stops, costs):
                writer.writerow([alpha, early_stop, cost])
    else:
        with open(file, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for early_stop, cost in zip(early_stops, costs):
                writer.writerow([alpha, early_stop, cost])
        
if __name__ == '__main__':
    main()
