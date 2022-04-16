import numpy as np
from numpy import linalg as la
import math
import pandas as pd
import itertools

def transform_coordinate_to_csv(input=None):
    node1=[]
    node2=[]
    weight=[]
    for i in range(len(input)):
        for j in range(i,len(input)):
            if i != j:
                dist = la.norm(input[i]-input[j])
                node1.append(i)
                node2.append(j)
                weight.append(dist)

    df = pd.DataFrame({'node1': node1,
                       'node2': node2,
                       'weight': weight})
    df.to_csv('graph.csv',index=False)

def read_graph_from_csv():
    df = pd.read_csv('graph.csv', encoding='unicode_escape')
    return df

def check_nodes_in_df(input, df_bidirectional, num_nodes):
    weight = 0.0
    for i in range(num_nodes):
        node1 = input[i]
        node2 = input[i+1]
        temp = df_bidirectional.loc[
            (df_bidirectional['node1'] == node1) & (df_bidirectional['node2'] == node2)].to_numpy()
        weight += temp[0, 2]
    return weight

def TSP():
    df = read_graph_from_csv()
    num_nodes = df[['node1','node2']].max().max()+1
    print(f"Graph:\n{df}")
    print(f"number of nodes: {num_nodes}")
    index_list = np.asarray(range(num_nodes))
    permutation_arr = np.asarray(list(itertools.permutations(index_list[1:])))
    temp_arr = np.empty(shape=[0, num_nodes-1])
    temp_arr = np.append(temp_arr, [permutation_arr[0]], axis=0)

    # print(len(permutation_arr))

    for i in permutation_arr:
        if ((temp_arr == np.flip(i)).all(1).any()) or ((temp_arr == i).all(1).any()):
            continue
        else:
            temp_arr = np.append(temp_arr, [i.copy()], axis=0)
    
    solution_arr = np.zeros((len(temp_arr),1))
    solution_arr = np.append(solution_arr, temp_arr, axis = 1)
    solution_arr = np.append(solution_arr, np.zeros((len(temp_arr),1)), axis=1).astype(np.int8)

    print(f"number of tours: {len(solution_arr)}")
    edge_temp = df[['node1','node2']].to_numpy()
    EDGES = np.append(edge_temp,df[['node2','node1']].to_numpy(), axis=0)
    weights_temp = df['weight'].to_numpy()
    weights = np.append(weights_temp,df['weight'].to_numpy())
    df_bidirectional = pd.DataFrame({'node1': EDGES[:,0], 'node2': EDGES[:,1], 'weight': weights})
    
    minimum_cost=np.Inf
    solution_weight_sum = []
    opt_solution_cnt = 0
    solution_weight_sum = np.apply_along_axis(func1d=check_nodes_in_df, axis=1, arr = solution_arr, df_bidirectional = df_bidirectional, num_nodes = num_nodes)
    minimum_cost = np.min(solution_weight_sum)

    if len(solution_weight_sum) <= 50:
        for i in range(len(solution_weight_sum)):
            print(f"solution {i+1}: {solution_arr[i].tolist()}, total_weight: {solution_weight_sum[i]}")

    print(f"minimum cost = {minimum_cost}")
    result = np.isclose(solution_weight_sum , minimum_cost)
    indices = np.where(result==True)
    opt_solution_cnt = len(indices)
    for i in indices:
        print(f"optimal solution: {solution_arr[i]}")
    print(f"number of optimal solutions: {opt_solution_cnt}")
    print(f"probability of finding an optimum tour when generating a tour at random: {float(opt_solution_cnt)/len(solution_arr)}")

def nearest_neighbour_heuristic(starting_city=None):
    df = read_graph_from_csv()
    num_nodes = df[['node1', 'node2']].max().max() + 1
    print(f"Graph:\n{df}")
    print(f"number of nodes: {num_nodes}\nnumber of edges: {len(df)}")
    edge_temp = df[['node1', 'node2']].to_numpy()
    EDGES = np.append(edge_temp, df[['node2', 'node1']].to_numpy(), axis=0)
    weights_temp = df['weight'].to_numpy()
    weights = np.append(weights_temp, df['weight'].to_numpy())
    df_bidirectional = pd.DataFrame({'node1': EDGES[:, 0], 'node2': EDGES[:, 1], 'weight': weights})
    tour_list=[]
    tour_list.append(starting_city)
    tour_list_index=0
    cnt=len(tour_list)
    
    while cnt < num_nodes:
        temp = df_bidirectional.loc[
            (df_bidirectional['node1'] == tour_list[tour_list_index]) & (~df_bidirectional['node2'].isin(tour_list))].to_numpy()
        print(temp)
        next_node_id = temp[:,2].argmin()
        tour_list.append(int(temp[next_node_id,1]))
        cnt = len(tour_list)
        tour_list_index = cnt - 1

    tour_list.append(starting_city)
    tour_list = np.asarray(tour_list)
    print(f"the tour from nearest_neighbour_heuristic:({starting_city} is the first node)\n{tour_list}")
    print(f"total cost: {check_nodes_in_df(tour_list, df_bidirectional, num_nodes)}")

def insersion_heuristic(starting_cities=None):
    df = read_graph_from_csv()
    num_nodes = df[['node1', 'node2']].max().max() + 1
    print(f"Graph:\n{df}")
    print(f"number of nodes: {num_nodes}\nnumber of edges: {len(df)}\n\n")
    edge_temp = df[['node1', 'node2']].to_numpy()
    EDGES = np.append(edge_temp, df[['node2', 'node1']].to_numpy(), axis=0)
    weights_temp = df['weight'].to_numpy()
    weights = np.append(weights_temp, df['weight'].to_numpy())
    df_bidirectional = pd.DataFrame({'node1': EDGES[:, 0], 'node2': EDGES[:, 1], 'weight': weights})
    tour_list = starting_cities.copy()
    tour_list_index = 0
    cnt = len(tour_list)

    while cnt < num_nodes:
        choices = {}
        minimum_weight = np.Inf
        next_city = 0
        unvisited_city = set(range(num_nodes)) ^ set(tour_list)
        for i in unvisited_city:
            for j in range(1,len(tour_list)):
                if len(choices) == 0:
                    choices[0] = np.insert(tour_list, j, i)
                    minimum_weight = check_nodes_in_df(choices[0], df_bidirectional, len(set(choices[0])))
                    next_city = i
                else:
                    temp = np.insert(tour_list, j, i)
                    temp_w = check_nodes_in_df(temp, df_bidirectional, len(set(temp)))
                    if temp_w < minimum_weight:
                        choices[0] = temp
                        minimum_weight = temp_w
                        next_city = i

        tour_list = choices[0].copy()
        cnt = len(tour_list) - 1
        print(f"next city: {next_city}")
        print(f"updated tour: {tour_list}")

    print(f"\n\nthe tour from insersion_heuristic:({tour_list[0]} is the first node)\n{tour_list}")
    print(f"total cost: {check_nodes_in_df(tour_list, df_bidirectional, num_nodes)}")

def two_change_TSP(input_config=None):
    print(f"initial config: {input_config}")
    df = read_graph_from_csv()
    num_nodes = df[['node1', 'node2']].max().max() + 1
    print(f"Graph:\n{df}")
    print(f"number of nodes: {num_nodes}\nnumber of edges: {len(df)}")
    edge_temp = df[['node1', 'node2']].to_numpy()
    EDGES = np.append(edge_temp, df[['node2', 'node1']].to_numpy(), axis=0)
    weights_temp = df['weight'].to_numpy()
    weights = np.append(weights_temp, df['weight'].to_numpy())
    df_bidirectional = pd.DataFrame({'node1': EDGES[:, 0], 'node2': EDGES[:, 1], 'weight': weights})
    result_tour_list=[]

    for i in range(num_nodes):
        node1 = input_config[i]
        node2 = input_config[i + 1]
        set1 = set([node1,node2])
        for j in range(i,num_nodes):
            node3 = input_config[j]
            node4 = input_config[j + 1]
            set2 = set([node3,node4])
            set_temp = set1 & set2
            if len(set_temp) == 0:
                temp=input_config.copy()
                temp[i+1:j+1] = np.flip(input_config[i+1:j+1])
                temp[i + 1] = node3
                temp[j] = node2
                result_tour_list.append(temp.tolist())
    result_tour_list = np.asarray(result_tour_list, dtype=np.int8)
    print(f"neighbours generated from two-change method:\n{result_tour_list}")
    solution_weight_sum = np.apply_along_axis(func1d=check_nodes_in_df, axis=1, arr=result_tour_list,
                                              df_bidirectional=df_bidirectional, num_nodes=num_nodes)
    minimum_cost = np.min(solution_weight_sum)
    if len(solution_weight_sum) <= 50:
        for i in range(len(solution_weight_sum)):
            print(f"solution {i+1}: {result_tour_list[i].tolist()}, total_weight: {solution_weight_sum[i]}")
    print(f"minimum cost of the neighbours: {minimum_cost}")
    return result_tour_list
    
# EXECUTION_________________________
'''
if there are given coordinates for cities, produce a csv file for graph first!!
X is the coordinates for cities

X = np.asarray([
    [4,11],
    [15,10],
    [10,5],
    [25,10],
    [35,10],
    [46,11],
    [20,5],
    [30,5],
    [40,5]
], dtype=np.float32)

transform_coordinate_to_csv(X)

'''

'''
Execute TSP()

TSP()
'''

'''
calculate the nearest_neighbour_heuristic tour with given starting_city which is a number

nearest_neighbour_heuristic(starting_city=0)
'''

'''
calculate the two-change neighbourhoods with given an input configuration which is a tour
two_change_TSP(input_config=np.asarray([0,1,2,3,4,0]))
# two_change_TSP(input_config=np.asarray([0, 2, 1, 6, 3, 7, 4, 8, 5, 0]))
'''

'''
calculate the nearest_neighbour_heuristic tour with given starting_cities which is a tour
insersion_heuristic(starting_cities=np.asarray([0,2,1,0]))
'''

